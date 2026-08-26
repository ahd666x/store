import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.cart.models import Cart, CartItem
from apps.catalog.models import Part, Product, Color, ColorMaterialMap
from apps.orders.models import Order, OrderItem, Customer, ProductionTask
from apps.orders.production_utils import (
    compute_size_diff, apply_size_adjustment, update_barcode_size,
    get_painting_process_for_color, get_item_color_assignments,
)

logger = logging.getLogger(__name__)


class InsufficientStockError(Exception):
    pass


def validate_cart_stock(user):
    cart = get_object_or_404(Cart, user=user)
    errors = []
    for item in cart.items.all():
        if item.product.stock < item.quantity:
            errors.append(f"موجودی {item.product.name} فقط {item.product.stock} عدد است.")
    if errors:
        raise InsufficientStockError("\n".join(errors))
    return cart


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, shipping_address):
        cart = get_object_or_404(Cart, user=user)

        if not cart.items.exists():
            raise ValueError("سبد خرید شما خالی است.")

        customer, _ = Customer.objects.get_or_create(
            user=user,
            defaults={
                'name': user.get_full_name() or user.username,
                'phone': getattr(user, 'phone', '') or '',
            }
        )

        order = Order.objects.create(
            user=user,
            customer=customer,
            shipping_address=shipping_address,
            total_amount=cart.total_price,
            final_amount=cart.final_price if cart.discount else cart.total_price,
            discount_amount=cart.discount_amount,
            discount=cart.discount,
            status='draft',
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                length=cart_item.custom_length,
                width=cart_item.custom_width,
                height=cart_item.custom_height,
            )

        try:
            OrderService.generate_production_tasks(order)
        except Exception:
            logger.exception("Error generating production tasks for order %s", order.id)

        cart.items.all().delete()
        cart.discount = None
        cart.save(update_fields=['discount'])
        return order

    @staticmethod
    @transaction.atomic
    def add_cart_items_to_order(order, cart):
        if not cart.items.exists():
            raise ValueError("سبد خرید شما خالی است.")

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                length=cart_item.custom_length,
                width=cart_item.custom_width,
                height=cart_item.custom_height,
            )

        try:
            OrderService.generate_production_tasks(order)
        except Exception:
            logger.exception("Error generating production tasks for order %s", order.id)

        order.discount = cart.discount
        order.discount_amount = cart.discount_amount
        order.total_amount = cart.total_price
        order.final_amount = cart.final_price
        order.save(update_fields=['discount', 'discount_amount', 'total_amount', 'final_amount'])

        cart.items.all().delete()
        cart.discount = None
        cart.save(update_fields=['discount'])

    @staticmethod
    @transaction.atomic
    def generate_production_tasks(order):
        tasks_to_create = []
        current_step = 0

        for item in order.items.all():
            item_colors = {c.part: c.code for c in item.ordercolor.all()}
            size_diff = compute_size_diff(item.product, item)

            for bom_entry in item.product.bom.all():
                part = bom_entry.part
                total_qty = bom_entry.quantity * item.quantity
                material = part.material

                if bom_entry.allow_material_override and bom_entry.color_part:
                    color_code = item_colors.get(bom_entry.color_part)
                    if color_code:
                        color_obj = Color.objects.filter(code=color_code).first()
                        if color_obj:
                            resolved = ColorMaterialMap.resolve_material(color_obj, item.product.category)
                            if resolved:
                                material = resolved

                length, width = part.length, part.width
                if bom_entry.size_affected and bom_entry.size_adjustment_rule and size_diff:
                    length, width = apply_size_adjustment(part.length, part.width, size_diff, bom_entry.size_adjustment_rule)

                new_f3 = update_barcode_size(part.f3, length, width, item.id)

                dynamic_part, created = Part.objects.get_or_create(
                    base_part=part, material=material, length=length, width=width, f3=new_f3,
                    defaults={
                        'name': part.name, 'grain': part.grain, 'pname': part.pname, 'turn': part.turn,
                        'f26': part.f26, 'f18': part.f18, 'f4': part.f4, 'f5': part.f5,
                        'f3': new_f3, 'f2': part.f2, 'routing_code': part.routing_code,
                    }
                )
                if not created and dynamic_part.f3 != new_f3:
                    dynamic_part.f3 = new_f3
                    dynamic_part.save(update_fields=['f3'])

                stations = [s.strip() for s in dynamic_part.routing_code.split('.') if s.strip()]
                if not stations or stations[0].lower() != 'cut':
                    if 'cut' not in [s.lower() for s in stations]:
                        stations.insert(0, 'cut')

                for idx, station_name in enumerate(stations):
                    current_step += 1
                    tasks_to_create.append(ProductionTask(
                        order=order, part=dynamic_part, station_name=station_name.lower(),
                        step_order=current_step, quantity=total_qty,
                        status='pending' if idx == 0 else 'waiting',
                    ))

        for item in order.items.all():
            for part_name, color_code in get_item_color_assignments(item):
                process = get_painting_process_for_color(color_code)
                if not process:
                    continue

                base_step = current_step
                stages = process.stages.all().order_by('order')
                for idx, stage in enumerate(stages, start=1):
                    tasks_to_create.append(ProductionTask(
                        order=order, part=None, station_name='paint',
                        step_order=base_step + idx, quantity=item.quantity,
                        status='pending' if idx == 1 else 'waiting',
                        painting_stage=stage, order_item=item, color_part=part_name,
                    ))
                current_step = base_step + stages.count()

        if tasks_to_create:
            ProductionTask.objects.bulk_create(tasks_to_create)
            order.status = 'planned'
            order.save(update_fields=['status'])
            return True
        return False

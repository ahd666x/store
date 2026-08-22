from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem


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
                'phone': getattr(user, 'phone', ''),
            }
        )

        order = Order.objects.create(
            user=user,
            customer=customer,
            shipping_address=shipping_address,
            total_amount=cart.total_price,
            final_amount=cart.final_price if cart.discount else cart.total_price,
            discount_amount=cart.discount_amount,
            status='draft',
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
            )

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
                unit_price=cart_item.product.price,
            )

        order.discount = cart.discount
        order.discount_amount = cart.discount_amount
        order.total_amount = cart.total_price
        order.final_amount = cart.final_price
        order.save(update_fields=['discount', 'discount_amount', 'total_amount', 'final_amount'])

        cart.items.all().delete()
        cart.discount = None
        cart.save(update_fields=['discount'])

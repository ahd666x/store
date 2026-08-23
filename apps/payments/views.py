from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, F
from django.db import transaction
from .models import Payment, Transaction
from apps.orders.models import Order
from apps.discounts.models import Discount
from .gateways import PaymentGatewayFactory


@login_required
def payment_create(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.final_amount,
            'gateway': getattr(settings, 'DEFAULT_PAYMENT_GATEWAY', 'zarinpal'),
        }
    )
    if not created and payment.status == 'success':
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        gateway = request.POST.get('gateway', payment.gateway)
        payment.gateway = gateway
        payment.save(update_fields=['gateway'])

    gateway = PaymentGatewayFactory.get(payment.gateway)
    result = gateway.pay(request, payment)
    if result.get('success'):
        if request.method == 'GET':
            return render(request, 'payments/payment_create.html', {'order': order, 'payment': payment})
        return redirect(result['url'])
    return render(request, 'payments/payment_error.html', {'error': result.get('error')})


@login_required
def payment_verify(request):
    authority = request.GET.get('Authority')
    gateway = request.GET.get('gateway')
    payment = None

    if gateway == 'cash_on_delivery':
        payment_id = request.GET.get('payment_id')
        if payment_id:
            payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
        else:
            return redirect('cart:cart_detail')
    else:
        payment = get_object_or_404(Payment, authority=authority, order__user=request.user)

    order = payment.order

    if gateway == 'cash_on_delivery':
        expected_amount = order.final_amount
        if payment.amount != expected_amount:
            payment.status = 'failed'
            payment.save()
            return render(request, 'payments/payment_error.html', {
                'error': f'مبلغ پرداخت ({payment.amount}) با مبلغ سفارش ({expected_amount}) مطابقت ندارد.'
            })

        gateway_obj = PaymentGatewayFactory.get('cash_on_delivery')
        result = gateway_obj.verify(request, payment)
        if result.get('success'):
            payment.status = 'success'
            payment.transaction_id = result.get('ref_id', '')
            payment.paid_at = timezone.now()
            payment.save()

            Transaction.objects.create(
                payment=payment,
                amount=payment.amount,
                ref_id=result.get('ref_id', ''),
                card_pan=result.get('card_pan', ''),
            )

            order.status = 'paid'
            order.paid_at = payment.paid_at
            order.save(update_fields=['status', 'paid_at'])

            if order.discount_id:
                with transaction.atomic():
                    discount = Discount.objects.select_for_update().get(pk=order.discount_id)
                    if discount.is_valid:
                        discount.used_count = F('used_count') + 1
                        discount.save(update_fields=['used_count'])

            for item in order.items.all():
                product = item.product
                if product.stock >= item.quantity:
                    product.stock = F('stock') - item.quantity
                    product.save(update_fields=['stock'])

            return redirect('orders:order_detail', order_id=order.id)
        return render(request, 'payments/payment_error.html', {'error': result.get('error')})

    expected_amount = order.final_amount
    if payment.amount != expected_amount:
        payment.status = 'failed'
        payment.save()
        return render(request, 'payments/payment_error.html', {
            'error': f'مبلغ پرداخت ({payment.amount}) با مبلغ سفارش ({expected_amount}) مطابقت ندارد.'
        })

    gateway_obj = PaymentGatewayFactory.get(payment.gateway)
    result = gateway_obj.verify(request, payment)
    if result.get('success'):
        payment.status = 'success'
        payment.transaction_id = result.get('ref_id', '')
        payment.paid_at = timezone.now()
        payment.save()

        Transaction.objects.create(
            payment=payment,
            amount=payment.amount,
            ref_id=result.get('ref_id', ''),
            card_pan=result.get('card_pan', ''),
        )

        order.status = 'paid'
        order.paid_at = payment.paid_at
        order.save(update_fields=['status', 'paid_at'])

        if order.discount_id:
            with transaction.atomic():
                discount = Discount.objects.select_for_update().get(pk=order.discount_id)
                if discount.is_valid:
                    discount.used_count = F('used_count') + 1
                    discount.save(update_fields=['used_count'])

        for item in order.items.all():
            product = item.product
            if product.stock >= item.quantity:
                product.stock = F('stock') - item.quantity
                product.save(update_fields=['stock'])

        return redirect('orders:order_detail', order_id=order.id)
    else:
        payment.status = 'failed'
        payment.save()
        return render(request, 'payments/payment_error.html', {'error': result.get('error')})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from .models import Payment
from apps.orders.models import Order
from .gateways.zarinpal import ZarinpalGateway


@login_required
def payment_create(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment, created = Payment.objects.get_or_create(order=order, defaults={'amount': order.final_amount})
    if not created and payment.status == 'success':
        return redirect('orders:order_detail', order_id=order.id)
    gateway = ZarinpalGateway()
    result = gateway.pay(request, payment)
    if result.get('success'):
        return redirect(result['url'])
    return render(request, 'payments/payment_error.html', {'error': result.get('error')})


@login_required
def payment_verify(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    payment = get_object_or_404(Payment, authority=authority, order__user=request.user)
    if status == 'OK':
        gateway = ZarinpalGateway()
        result = gateway.verify(request, payment)
        if result.get('success'):
            payment.status = 'success'
            payment.transaction_id = result.get('ref_id', '')
            payment.paid_at = timezone.now()
            payment.save()

            order = payment.order
            order.status = 'paid'
            order.paid_at = payment.paid_at
            order.save()

            for item in order.items.all():
                product = item.product
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save(update_fields=['stock'])

            return redirect('orders:order_detail', order_id=payment.order.id)
        else:
            payment.status = 'failed'
            payment.save()
            return render(request, 'payments/payment_error.html', {'error': result.get('error')})
    else:
        payment.status = 'cancelled'
        payment.save()
        return redirect('cart:cart_detail')

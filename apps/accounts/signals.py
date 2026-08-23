from django.contrib.auth.signals import user_logged_in
from django.db.models import Sum
from django.dispatch import receiver
from .models import User
from apps.cart.models import Cart, CartItem


@receiver(user_logged_in)
def merge_guest_cart_on_login(sender, request, user, **kwargs):
    session_key = getattr(request.session, 'session_key', None)
    if not session_key:
        return
    session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
    if not session_cart:
        return

    user_cart, created = Cart.objects.get_or_create(user=user)

    for item in session_cart.items.all():
        existing = user_cart.items.filter(product=item.product).first()
        if existing:
            existing.quantity = existing.quantity + item.quantity
            existing.save(update_fields=['quantity'])
        else:
            item.cart = user_cart
            item.save(update_fields=['cart'])

    session_cart.delete()

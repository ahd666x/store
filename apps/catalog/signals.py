from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, StockAlert

@receiver(pre_save, sender=Product)
def track_stock_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Product.objects.get(pk=instance.pk)
            instance._old_stock = old.stock
        except Product.DoesNotExist:
            instance._old_stock = None
    else:
        instance._old_stock = None

@receiver(post_save, sender=Product)
def notify_stock_alerts(sender, instance, created, **kwargs):
    if created:
        return
    old_stock = getattr(instance, '_old_stock', None)
    if old_stock is not None and old_stock == 0 and instance.stock > 0:
        alerts = StockAlert.objects.filter(product=instance, is_notified=False).select_related('user')
        for alert in alerts:
            try:
                send_mail(
                    subject=f'موجودی {instance.name} برگشت!',
                    message=f'محصول {instance.name} دوباره موجود شد. از طریق لینک زیر خرید کنید:\n{settings.SITE_URL}/catalog/products/{instance.slug}/',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[alert.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            alert.is_notified = True
            alert.save(update_fields=['is_notified'])

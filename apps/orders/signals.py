from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from .models import Order
from apps.communications.models import Notification

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='push',
            subject=f'سفارش #{instance.id} ثبت شد',
            message=f'سفارش شما با مبلغ {instance.final_amount} تومان ثبت شد.',
        )

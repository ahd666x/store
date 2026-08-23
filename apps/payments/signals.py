from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from apps.communications.models import Notification

@receiver(post_save, sender=Payment)
def create_payment_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.order.user,
            notification_type='email',
            subject=f'پرداخت سفارش #{instance.order.id}',
            message=f'پرداخت شما به مبلغ {instance.amount} تومان در وضعیت {instance.get_status_display()} قرار گرفت.',
        )

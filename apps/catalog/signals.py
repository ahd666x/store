from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, StockAlert, ProductSection, ColorMaterialMap, Part


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


@receiver(pre_save, sender=ProductSection)
def track_section_color_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = ProductSection.objects.get(pk=instance.pk)
            instance._old_color_id = old.color_id
        except ProductSection.DoesNotExist:
            instance._old_color_id = None
    else:
        instance._old_color_id = None


@receiver(post_save, sender=ProductSection)
def update_parts_material_on_color_change(sender, instance, created, **kwargs):
    if created:
        return
    old_color_id = getattr(instance, '_old_color_id', None)
    if old_color_id is not None and old_color_id != instance.color_id:
        parts = instance.parts.filter(material_override=False)
        for part in parts:
            resolved = ColorMaterialMap.resolve_material(instance.color, instance.product.category)
            if resolved:
                part.material = resolved
                part.save(update_fields=['material'])


@receiver(pre_save, sender=Part)
def resolve_part_material(sender, instance, **kwargs):
    if not instance.section_id:
        return
    old_material_id = None
    if instance.pk:
        try:
            old = Part.objects.get(pk=instance.pk)
            old_material_id = old.material_id
        except Part.DoesNotExist:
            pass
    if instance.material_id is None or instance.material_id == old_material_id:
        color = instance.section.color
        mapping = ColorMaterialMap.objects.filter(color=color).first()
        if mapping:
            instance.material = mapping.material

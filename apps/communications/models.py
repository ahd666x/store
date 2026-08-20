from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User


class EmailTemplate(BaseModel):
    TEMPLATE_TYPE_CHOICES = [
        ('welcome', 'خوش‌آمدگویی'),
        ('order_confirmation', 'تایید سفارش'),
        ('payment_success', 'موفقیت پرداخت'),
        ('password_reset', 'بازنشانی رمز عبور'),
    ]

    name = models.CharField(max_length=100, verbose_name="نام")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    body = models.TextField(verbose_name="متن")
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES, verbose_name="نوع")

    class Meta:
        verbose_name = "قالب ایمیل"
        verbose_name_plural = "قالب‌های ایمیل"

    def __str__(self):
        return self.name


class Notification(BaseModel):
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'ایمیل'),
        ('sms', 'پیامک'),
        ('push', 'پوش'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="کاربر")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name="نوع")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    message = models.TextField(verbose_name="پیام")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"

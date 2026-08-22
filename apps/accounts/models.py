from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.common.models import BaseModel
import random


class User(AbstractUser, BaseModel):
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="تلفن")
    email = models.EmailField(unique=True, verbose_name="ایمیل")

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.username


class OTPCode(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="کاربر")
    phone = models.CharField(max_length=15, verbose_name="شماره موبایل")
    code = models.CharField(max_length=6, verbose_name="کد OTP")
    is_used = models.BooleanField(default=False, verbose_name="استفاده شده")
    expires_at = models.DateTimeField(verbose_name="زمان انقضا")

    class Meta:
        verbose_name = "کد OTP"
        verbose_name_plural = "کدهای OTP"
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP {self.phone} - {self.code}"

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

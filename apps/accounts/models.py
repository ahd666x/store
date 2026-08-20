from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import BaseModel

class User(AbstractUser, BaseModel):
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="تلفن")
    email = models.EmailField(unique=True, verbose_name="ایمیل")

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.username

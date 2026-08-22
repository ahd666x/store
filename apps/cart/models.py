from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User
from apps.catalog.models import Product


class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name="کاربر")
    discount = models.ForeignKey('discounts.Discount', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تخفیف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"سبد خرید {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def discount_amount(self):
        if not self.discount or not self.discount.is_valid:
            return 0
        total = self.total_price
        if self.discount.discount_type == 'percent':
            return int(total * self.discount.value / 100)
        return min(self.discount.value, total)

    @property
    def final_price(self):
        return max(self.total_price - self.discount_amount, 0)


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="سبد خرید")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity

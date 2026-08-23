from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product


class CartService:
    @staticmethod
    @transaction.atomic
    def add_item(cart, product_id, quantity=1, length=None, width=None, height=None):
        """
        آیتم را به سبد اضافه می‌کند. اگر ابعاد سفارشی داده نشود، ابعاد پیش‌فرض
        محصول جایگزین می‌شود (یعنی اختلاف قیمت صفر و قیمت = قیمت پایه) —
        این رفتار دکمه‌های «افزودن سریع» بدون فرم ابعاد را دست‌نخورده نگه می‌دارد.
        بازگشتی: (cart_item, capped) — capped=True یعنی تعداد به موجودی محدود شد.
        """
        product = get_object_or_404(Product, id=product_id)

        length = length if length is not None else product.length
        width = width if width is not None else product.width
        height = height if height is not None else product.height

        cart_item = CartItem.objects.filter(
            cart=cart, product=product,
            custom_length=length, custom_width=width, custom_height=height,
        ).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                cart=cart, product=product, quantity=quantity,
                custom_length=length, custom_width=width, custom_height=height,
            )

        capped = False
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
            capped = True

        cart_item.recalculate_price()
        cart_item.save()
        return cart_item, capped

    @staticmethod
    @transaction.atomic
    def remove_item(cart, product_id):
        # توجه: چون حالا ممکن است چند ردیف با ابعاد متفاوت از یک محصول در سبد
        # باشد، این متد همه‌ی ردیف‌های آن محصول را حذف می‌کند (نه فقط یکی).
        # اگر بعداً حذف دقیق هر ابعاد جداگانه لازم شد، باید URL/ویو cart_remove
        # را از product_id به cart_item_id تغییر داد.
        deleted, _ = CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return deleted

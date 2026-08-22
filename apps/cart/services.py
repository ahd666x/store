from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product


class CartService:
    @staticmethod
    @transaction.atomic
    def add_item(cart, product_id, quantity=1):
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
        cart_item.save()
        return cart_item

    @staticmethod
    @transaction.atomic
    def remove_item(cart, product_id):
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()

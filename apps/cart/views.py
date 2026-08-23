from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Cart, CartItem
from .services import CartService
from apps.catalog.models import Product


def _get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


def cart_detail(request):
    cart = _get_cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


def _parse_dim(request, name):
    raw = request.POST.get(name)
    if raw in (None, ''):
        return None
    try:
        value = int(raw)
        return value if value > 0 else None
    except (TypeError, ValueError):
        return None


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)

    try:
        quantity = max(1, int(request.POST.get('quantity', 1)))
    except (TypeError, ValueError):
        quantity = 1

    length = _parse_dim(request, 'length')
    width = _parse_dim(request, 'width')
    height = _parse_dim(request, 'height')

    cart_item, capped = CartService.add_item(
        cart, product_id, quantity, length=length, width=width, height=height
    )

    if capped:
        messages.error(request, f"موجودی {product.name} فقط {product.stock} عدد است.")
    messages.success(request, 'محصول به سبد خرید اضافه شد.')

    if request.headers.get('HX-Request'):
        cart_count = cart.items.count()
        return HttpResponse(f'<span id="cart-count" class="absolute -top-2 -start-3 bg-primary-600 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">{cart_count}</span>')

    return redirect('catalog:product_list')


def cart_remove(request, product_id):
    cart = _get_cart(request)
    CartService.remove_item(cart, product_id)
    messages.success(request, 'محصول از سبد خرید حذف شد.')
    return redirect('cart:cart_detail')


def cart_update(request, product_id):
    cart = _get_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    try:
        new_quantity = int(request.POST.get('quantity', cart_item.quantity))
    except (TypeError, ValueError):
        new_quantity = cart_item.quantity

    product = cart_item.product
    if new_quantity > product.stock:
        new_quantity = product.stock
    if new_quantity < 1:
        new_quantity = 1

    cart_item.quantity = new_quantity
    cart_item.recalculate_price()
    cart_item.save()

    if request.headers.get('HX-Request'):
        return render(request, 'cart/includes/cart_item_row.html', {'item': cart_item, 'cart': cart})

    messages.success(request, 'تعداد به‌روزرسانی شد.')
    return redirect('cart:cart_detail')

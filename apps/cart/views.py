from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Cart, CartItem
from .services import CartService
from apps.catalog.models import Product


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
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


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

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
        return HttpResponse(f'<span id="cart-count" class="mr-1 bg-indigo-100 text-indigo-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">{cart_count}</span>')

    return redirect('catalog:product_list')


@login_required
def cart_remove(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    CartService.remove_item(cart, product_id)
    messages.success(request, 'محصول از سبد خرید حذف شد.')
    return redirect('cart:cart_detail')

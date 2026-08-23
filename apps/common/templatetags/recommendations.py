from django import template
from apps.catalog.models import Product
from django.db.models import Q, Avg, Count

register = template.Library()

@register.filter
def recommend_products(user):
    if not user.is_authenticated:
        return Product.active_objects.none()
    
    from apps.cart.models import Cart
    from apps.accounts.models import Wishlist
    
    cart = Cart.objects.filter(user=user).first()
    wishlist = Wishlist.objects.filter(user=user).first()
    
    product_ids = set()
    if cart:
        product_ids.update(cart.items.values_list('product_id', flat=True))
    if wishlist:
        product_ids.update(wishlist.items.values_list('product_id', flat=True))
    
    if not product_ids:
        return Product.active_objects.filter(stock__gt=0).order_by('-created_at')[:8]
    
    categories = Product.objects.filter(id__in=product_ids).values_list('category', flat=True).distinct()
    
    return Product.active_objects.filter(
        category__in=categories
    ).exclude(id__in=product_ids).prefetch_related('images').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
        rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
    ).order_by('-avg_rating', '-created_at')[:8]

from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from .models import Product, Category


class CatalogService:
    @staticmethod
    def search_products(query):
        return Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True,
        )

    @staticmethod
    def get_featured_products(limit=8):
        return Product.objects.filter(is_active=True, stock__gt=0).order_by('-created_at')[:limit]

    @staticmethod
    def get_category_products(category_slug):
        return Product.objects.filter(category__slug=category_slug, is_active=True)

    @staticmethod
    def calculate_inventory_value():
        return Product.objects.filter(is_active=True).aggregate(
            total_value=Sum(F('price') * F('stock'), output_field=DecimalField())
        )['total_value'] or 0

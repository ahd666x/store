from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from .models import Product, ProductCategory


class CatalogService:
    @staticmethod
    def search_products(query):
        return Product.active_objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
        )

    @staticmethod
    def get_featured_products(limit=8):
        return Product.active_objects.filter(stock__gt=0).order_by('-created_at')[:limit]

    @staticmethod
    def get_category_products(category_slug):
        return Product.active_objects.filter(category__slug=category_slug)

    @staticmethod
    def calculate_inventory_value():
        return Product.active_objects.aggregate(
            total_value=Sum(F('price') * F('stock'), output_field=DecimalField())
        )['total_value'] or 0

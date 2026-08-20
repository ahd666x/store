from django.contrib import admin
from .models import ProductCategory, Color, Material, Product, ProductSection, Piece, Part, ProductBOM


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'thickness']
    search_fields = ['name']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class ProductSectionInline(admin.TabularInline):
    model = ProductSection
    extra = 1
    fields = ['name', 'color', 'description']


class PieceInline(admin.TabularInline):
    model = Piece
    extra = 1
    fields = ['length', 'width', 'description']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'length', 'width', 'height', 'default_size', 'base_price', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [ProductSectionInline]


@admin.register(ProductSection)
class ProductSectionAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'color']
    list_filter = ['product__category', 'color']
    search_fields = ['name', 'product__name']
    inlines = [PieceInline]


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'material', 'length', 'width', 'pname', 'routing_code']
    list_filter = ['material', 'pname']
    search_fields = ['name', 'f2', 'f3']


@admin.register(ProductBOM)
class ProductBOMAdmin(admin.ModelAdmin):
    list_display = ['product', 'part', 'quantity', 'allow_material_override', 'size_affected']
    list_filter = ['product__category', 'allow_material_override', 'size_affected']
    search_fields = ['product__name', 'part__name']

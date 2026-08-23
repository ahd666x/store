from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import ProductCategory, Color, Material, Product, ProductImage, ProductReview, ProductSection, Part, ProductBOM, ColorMaterialMap


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
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ColorMaterialMap)
class ColorMaterialMapAdmin(admin.ModelAdmin):
    list_display = ['color', 'material']


class ProductSectionInline(admin.TabularInline):
    model = ProductSection
    extra = 1
    fields = ['name', 'color', 'description']


class PartInline(admin.TabularInline):
    model = Part
    extra = 1
    fields = ['name', 'material', 'length', 'width', 'routing_code']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text']


class ProductBOMInline(admin.TabularInline):
    model = ProductBOM
    fields = [
        'part',
        'quantity',
        'allow_material_override',
        'color_part',
        'color_material_map',
        'size_affected',
        'size_adjustment_rule',
    ]
    verbose_name = "قطعه فنی"
    verbose_name_plural = "لیست قطعات"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'stock', 'length', 'width', 'height', 'base_price', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSectionInline, ProductImageInline, ProductBOMInline]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('category', 'name', 'slug', 'color', 'description', 'base_price', 'price', 'stock', 'is_active')
        }),
        ('ابعاد و قیمت‌گذاری سفارشی', {
            'fields': (
                ('length', 'length_editable', 'length_price_percent'),
                ('width', 'width_editable', 'width_price_percent'),
                ('height', 'height_editable', 'height_price_percent'),
            )
        }),
        ('سایر', {
            'fields': ('default_size', 'default_colors', 'parts_list_key')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'alt_text']
    list_filter = ['product__category']
    search_fields = ['product__name', 'alt_text']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_active', 'created_at']
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']


@admin.register(ProductSection)
class ProductSectionAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'color']
    list_filter = ['product__category', 'color']
    search_fields = ['name', 'product__name']
    inlines = [PartInline]


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['f3', 'f2', 'material', 'length', 'width', 'routing_code']
    search_fields = ['f3', 'f2', 'routing_code']
    list_filter = ['material']


@admin.register(ProductBOM)
class ProductBOMAdmin(admin.ModelAdmin):
    list_display = ['product', 'part', 'quantity', 'size_affected']
    list_filter = ['product__category', 'size_affected']
    search_fields = ['product__name', 'part__name']

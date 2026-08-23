from django.contrib import admin
from .models import ProductCategory, Color, Material, Product, ProductImage, ProductReview, ProductSection, Piece, Part, ProductBOM, ColorMaterialMap


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
    list_display = ['color', 'material', 'category']
    list_filter = ['category']
    search_fields = ['color__name', 'material__name']


class ProductSectionInline(admin.TabularInline):
    model = ProductSection
    extra = 1
    fields = ['name', 'color', 'description']


class PieceInline(admin.TabularInline):
    model = Piece
    extra = 1
    fields = ['length', 'width', 'description']


class PartInline(admin.TabularInline):
    model = Part
    extra = 1
    fields = ['name', 'quantity', 'material', 'material_override', 'routing_code']
    readonly_fields = ['material']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'stock', 'length', 'width', 'height', 'base_price', 'is_active']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSectionInline, ProductImageInline]
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
    inlines = [PieceInline, PartInline]


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'material', 'section', 'length', 'width', 'pname', 'routing_code']
    list_filter = ['material', 'section', 'pname']
    search_fields = ['name', 'f2', 'f3']


@admin.register(ProductBOM)
class ProductBOMAdmin(admin.ModelAdmin):
    list_display = ['product', 'part', 'quantity', 'allow_material_override', 'size_affected']
    list_filter = ['product__category', 'allow_material_override', 'size_affected']
    search_fields = ['product__name', 'part__name']

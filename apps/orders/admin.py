from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Order, OrderItem, Customer, OrderColor, PackagingUnit, ProductionTask, ProductionLog, ShipmentLog


class ColorInline(admin.TabularInline):
    model = OrderColor
    fields = ['part', 'code']
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'quantity', 'size', 'notes', 'colors_link', 'print_order_link', 'print_lable_link']
    readonly_fields = ['colors_link', 'print_order_link', 'print_lable_link']
    extra = 1

    def colors_link(self, obj):
        if obj.pk:
            colors = obj.ordercolor.all()
            cc = "-".join([f"{c.part}{c.code}" for c in colors if c.code != 'nan'])
            if not cc:
                cc = "انتخاب رنگ"
            url = reverse('admin:orders_orderitem_change', args=[obj.id])
            return format_html('<a href="{}" target="_blank">{}</a>', url, cc)
        return "-"
    colors_link.short_description = 'رنگ'

    def print_order_link(self, obj):
        if obj.pk:
            url = reverse('production:print_sheet', args=[obj.id])
            return format_html('<a href="{}" target="_blank">چاپ فرم تولید</a>', url)
        return "-"
    print_order_link.short_description = 'فرم تولید'

    def print_lable_link(self, obj):
        if obj.pk:
            url = reverse('production:print_lable', args=[obj.id])
            return format_html('<a href="{}" target="_blank">چاپ لیبل</a>', url)
        return "-"
    print_lable_link.short_description = 'لیبل بسته‌بندی'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'user']
    search_fields = ['name', 'phone']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer', 'number', 'status', 'priority', 'final_amount', 'created_at', 'due_date']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['number', 'customer__name', 'tracking_code']
    inlines = [OrderItemInline]
    actions = ['generate_tasks_action']

    def generate_tasks_action(self, request, queryset):
        for order in queryset:
            if order.generate_tasks():
                self.message_user(request, f"  {order.id} ok ")
            else:
                self.message_user(request, f"سفارش {order.id} قبلاً صادر شده است.", level='warning')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'brc', 'created_at', 'user', 'category', 'product',
        'size', 'quantity', 'calculated_price', 'color_summary',
        'print_order_link', 'print_lable_link'
    ]
    readonly_fields = ['calculated_price', 'print_order_link', 'print_lable_link']
    list_filter = ['order__user', 'product__category', 'product']
    search_fields = ['order__user__username', 'product__name']
    list_per_page = 50
    inlines = [ColorInline]

    def user(self, obj):
        return obj.order.user
    user.short_description = 'نماینده'
    user.admin_order_field = 'order__user'

    def category(self, obj):
        return obj.product.category
    category.short_description = 'دسته'
    category.admin_order_field = 'product__category'

    def size(self, obj):
        return obj.product.default_size
    size.short_description = 'اندازه'

    def created_at(self, obj):
        return obj.order.created_at
    created_at.short_description = 'تاریخ'
    created_at.admin_order_field = 'order__created_at'

    def brc(self, obj):
        return f"{obj.order.id}.{obj.id}"
    brc.short_description = 'کد سفارش'

    def color_summary(self, obj):
        return obj.color_summary
    color_summary.short_description = 'رنگ'

    @admin.display(description='قیمت محاسبه‌شده)')
    def calculated_price(self, obj):
        return f"{obj.unit_price:,} ریال"

    def print_order_link(self, obj):
        if obj.pk:
            url = reverse('production:print_sheet', args=[obj.id])
            return format_html('<a href="{}" target="_blank">چاپ فرم تولید</a>', url)
        return "-"

    def print_lable_link(self, obj):
        if obj.pk:
            url = reverse('production:print_lable', args=[obj.id])
            return format_html('<a href="{}" target="_blank">چاپ لیبل</a>', url)
        return "-"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            obj.sync_packaging_units()


@admin.register(OrderColor)
class OrderColorAdmin(admin.ModelAdmin):
    list_display = ['orderitem', 'part', 'code']
    list_filter = ['part']
    search_fields = ['orderitem__product__name']


@admin.register(PackagingUnit)
class PackagingUnitAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_item_link',
        'unit_number',
        'is_packed',
        'is_shipped',
        'packed_at',
        'shipped_at',
    ]
    list_filter = [
        'is_packed',
        'is_shipped',
    ]
    search_fields = [
        'order_item__order__id',
        'order_item__product__name',
        'order_item__order__customer__name',
    ]
    readonly_fields = [
        'packed_at',
        'packed_by',
        'shipped_at',
        'shipped_by',
        'qr_code_preview',
    ]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('order_item', 'unit_number', 'qr_code_preview')
        }),
        ('وضعیت بسته‌بندی', {
            'fields': ('is_packed', 'packed_at', 'packed_by')
        }),
        ('وضعیت ارسال', {
            'fields': ('is_shipped', 'shipped_at', 'shipped_by')
        }),
    )

    @admin.display(description='آیتم سفارش')
    def order_item_link(self, obj):
        url = reverse('admin:orders_orderitem_change', args=[obj.order_item.id])
        return format_html('<a href="{}">{}</a>', url, obj.order_item)

    @admin.display(description='پیش‌نمایش QR')
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="100" height="100" />', obj.qr_code.url)
        return '-'


@admin.register(ProductionTask)
class ProductionTaskAdmin(admin.ModelAdmin):
    list_display = ['order', 'part', 'station_name', 'quantity', 'status', 'completed_at']
    list_filter = ['station_name', 'status']
    search_fields = ['part__f3', 'order__id']
    readonly_fields = ['scanned_by', 'completed_at']
    actions = ['save_tasks', 'save_tasks_pending']

    @admin.action(description="done")
    def save_tasks(self, request, queryset):
        for task in queryset:
            task.status = 'done'
            task.save()

    @admin.action(description="pending")
    def save_tasks_pending(self, request, queryset):
        for task in queryset:
            task.status = 'pending'
            task.save()


@admin.register(ProductionLog)
class ProductionLogAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'stage', 'user', 'created_at']
    list_filter = ['stage', 'order_item']


@admin.register(ShipmentLog)
class ShipmentLogAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'shipped_at', 'packaging_unit']

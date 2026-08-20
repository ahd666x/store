from django.contrib import admin
from .models import Order, OrderItem, Customer, OrderColor, PackagingUnit, ProductionTask, ProductionLog, ShipmentLog


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'user']
    search_fields = ['name', 'phone']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer', 'number', 'status', 'priority', 'final_amount', 'created_at', 'due_date']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['number', 'customer__name', 'tracking_code']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'size', 'unit_price']
    list_filter = ['order__status']
    search_fields = ['product__name', 'order__number']


@admin.register(OrderColor)
class OrderColorAdmin(admin.ModelAdmin):
    list_display = ['orderitem', 'part', 'code']
    list_filter = ['part']
    search_fields = ['orderitem__product__name']


@admin.register(PackagingUnit)
class PackagingUnitAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'unit_number', 'is_packed', 'is_shipped', 'packed_by', 'shipped_by']
    list_filter = ['is_packed', 'is_shipped']
    search_fields = ['order_item__product__name']


@admin.register(ProductionTask)
class ProductionTaskAdmin(admin.ModelAdmin):
    list_display = ['order', 'station_name', 'step_order', 'status', 'quantity', 'assigned_worker']
    list_filter = ['station_name', 'status']
    search_fields = ['order__number', 'part__name']


@admin.register(ProductionLog)
class ProductionLogAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'stage', 'user', 'created_at']
    list_filter = ['stage', 'created_at']
    search_fields = ['order_item__product__name', 'user__username']


@admin.register(ShipmentLog)
class ShipmentLogAdmin(admin.ModelAdmin):
    list_display = ['packaging_unit', 'plate_number', 'shipped_by', 'shipped_at']
    search_fields = ['plate_number', 'packaging_unit__order_item__product__name']

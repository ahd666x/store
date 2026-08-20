from django.contrib import admin
from .models import Payment, Transaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'status', 'gateway', 'created_at']
    list_filter = ['status', 'gateway', 'created_at']
    search_fields = ['order__id', 'transaction_id', 'authority']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'amount', 'ref_id']
    list_filter = ['payment__status']

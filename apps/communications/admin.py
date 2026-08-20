from django.contrib import admin
from .models import EmailTemplate, Notification


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'template_type']
    list_filter = ['template_type']
    search_fields = ['name', 'subject']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'subject', 'is_read', 'sent_at']
    list_filter = ['notification_type', 'is_read', 'sent_at']
    search_fields = ['user__username', 'subject']

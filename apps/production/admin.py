from django.contrib import admin
from .models import WorkerProfile, PaintingProcess, PaintingStage, PaintingAssignmentRule, Holiday


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'stage', 'is_available']
    list_filter = ['stage', 'is_available']
    search_fields = ['user__username']


@admin.register(PaintingProcess)
class PaintingProcessAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(PaintingStage)
class PaintingStageAdmin(admin.ModelAdmin):
    list_display = ['process', 'order', 'name', 'duration_minutes', 'drying_time_minutes']
    list_filter = ['process']
    search_fields = ['name', 'process__name']


@admin.register(PaintingAssignmentRule)
class PaintingAssignmentRuleAdmin(admin.ModelAdmin):
    list_display = ['worker', 'painting_stage', 'rule_type', 'priority', 'is_active']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['worker__user__username']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['date', 'description']
    list_filter = ['date']
    search_fields = ['description']

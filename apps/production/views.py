from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from apps.orders.models import ProductionTask


class ProductionTaskListView(LoginRequiredMixin, ListView):
    """
    داشبورد ساده وظایف تولید: نمایش تسک‌های در انتظار/در حال انجام
    بر اساس ایستگاه کاری کارگر لاگین‌شده (در صورت وجود پروفایل کارگر).
    """
    model = ProductionTask
    template_name = 'production/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 50

    def get_queryset(self):
        qs = ProductionTask.objects.select_related('order', 'part', 'order_item', 'assigned_worker')
        station = self.request.GET.get('station')
        if station:
            qs = qs.filter(station_name=station)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('order', 'step_order')

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, TemplateView
from django.db.models import Count, Q
from django.utils import timezone
from apps.orders.models import ProductionTask


def is_production_staff(user):
    return user.is_staff or user.is_superuser or hasattr(user, 'worker_profile')


class ProductionKanbanView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'production/kanban.html'
    login_url = 'accounts:login'

    def test_func(self):
        return is_production_staff(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.request.GET.get('station')
        qs = ProductionTask.objects.select_related('order', 'part', 'order_item', 'assigned_worker')
        if station:
            qs = qs.filter(station_name=station)

        context['stations'] = ProductionTask.STATION_CHOICES
        context['selected_station'] = station or ''
        context['tasks_waiting'] = qs.filter(status='waiting').order_by('order', 'step_order')
        context['tasks_pending'] = qs.filter(status='pending').order_by('order', 'step_order')
        context['tasks_done'] = qs.filter(status='done').order_by('-completed_at')[:50]
        return context


class ProductionReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'production/report.html'
    login_url = 'accounts:login'

    def test_func(self):
        return is_production_staff(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        report_date = self.request.GET.get('date', today.isoformat())

        tasks = ProductionTask.objects.filter(
            status='done',
            completed_at__date=report_date,
        ).select_related('scanned_by')

        report = {}
        for task in tasks:
            worker = task.scanned_by
            if not worker:
                continue
            key = worker.username
            if key not in report:
                report[key] = {
                    'worker': worker,
                    'total_tasks': 0,
                    'stations': {},
                }
            report[key]['total_tasks'] += 1
            station = task.get_station_name_display()
            report[key]['stations'][station] = report[key]['stations'].get(station, 0) + 1

        context['report'] = sorted(report.values(), key=lambda x: x['total_tasks'], reverse=True)
        context['report_date'] = report_date
        return context


class ProductionTaskListView(LoginRequiredMixin, ListView):
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

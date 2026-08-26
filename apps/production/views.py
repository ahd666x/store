import ast
import datetime as dt
import io
import json
import logging
import math
import os
import re
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from xml.dom import minidom

import jdatetime
import pandas as pd
from django.apps import apps
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db import models, transaction
from django.db.models import Count, Exists, F, IntegerField, OuterRef, Q, Subquery, Sum
from django.http import HttpResponse, HttpResponseForbidden, Http404, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import ListView, TemplateView
from django.forms import inlineformset_factory, modelformset_factory

from apps.accounts.models import User
from apps.catalog.models import Product, ProductCategory, Part, Color, Material, ProductBOM
from apps.orders.models import (
    Order, OrderItem, Customer, ProductionTask, PackagingUnit,
    ProductionLog, ShipmentLog, OrderColor,
)
from apps.production.models import (
    WorkerProfile, PaintingProcess, PaintingStage, PaintingAssignmentRule,
    Holiday, create_paint_tasks,
)
from apps.production.forms import (
    OrderEditForm, OrderItemForm, EditOrderItemForm, ColorSelectionForm,
    CustomerInfoForm, OrderCustomerForm, PartForm, ProductCreateForm,
    PaintingProcessForm, PaintingStageForm, WorkerProfileForm,
    OrderForm, ColorForm, CompleteOrderForm,
)
from apps.production.decorators import admin_or_manager_required, staff_or_representative_required
from apps.production.utils import (
    worker_to_dict,
    create_and_schedule_items_for_date,
    get_painting_ready_items_queryset,
    get_item_paint_preview,
    schedule_paint_tasks_for_items,
    schedule_paint_items_auto,
    auto_assign_paint_tasks,
    is_working_day,
    parse_jalali_date,
    _get_initial_item_cursors,
    _get_active_assignment_rules,
    repaint_item_ids_for_date,
    assign_task_to_worker,
    get_unique_color_codes_for_item,
    get_unscheduled_ready_items,
    painting_nav_context,
)
from apps.orders.production_utils import (
    get_item_color_assignments,
    get_painting_process_for_color,
)
from apps.common.permissions import is_production_staff

logger = logging.getLogger(__name__)


# ============================================================
# Painting Management API Views
# ============================================================

@login_required
@admin_or_manager_required
def painting_workers_api(request):
    if request.method == 'GET':
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        skill_filter = request.GET.get('skill', '')
        page = int(request.GET.get('page', 1))
        per_page = 20

        workers = WorkerProfile.objects.filter(stage='paint') \
            .select_related('user') \
            .prefetch_related('excluded_products') \
            .annotate(active_tasks=Count('user__assigned_tasks',
                filter=Q(user__assigned_tasks__station_name='paint',
                        user__assigned_tasks__status__in=['pending', 'waiting'])
            ))

        if search:
            workers = workers.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        if status_filter == 'active':
            workers = workers.filter(is_available=True)
        elif status_filter == 'inactive':
            workers = workers.filter(is_available=False)
        if skill_filter:
            workers = workers.filter(skills__contains=[skill_filter])

        paginator = Paginator(workers, per_page)
        page_obj = paginator.get_page(page)

        table_html = render_to_string('production/painting_management/_worker_rows.html', {
            'workers': page_obj,
            'skill_choices': PaintingStage.SKILL_CHOICES,
        })
        pagination_html = render_to_string('production/painting_management/_pagination.html', {
            'workers': page_obj,
        })

        return JsonResponse({
            'success': True,
            'table_html': table_html,
            'pagination_html': pagination_html,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages,
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            if not user_id:
                return JsonResponse({'success': False, 'error': 'کاربر انتخاب نشده است'})
            worker = WorkerProfile.objects.create(
                user_id=user_id,
                stage=data.get('stage', 'paint'),
                is_available=data.get('is_available', True),
                skills=data.get('skills', []),
                skill_priority=data.get('skill_priority', data.get('skill_costs', {}))
            )
            return JsonResponse({'success': True, 'worker': worker_to_dict(worker)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'روش غیرمجاز'})


@login_required
@admin_or_manager_required
@require_http_methods(['GET', 'PUT', 'DELETE'])
def painting_worker_detail_api(request, worker_id):
    worker = get_object_or_404(WorkerProfile, pk=worker_id, stage='paint')

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'id': worker.id,
            'user_id': worker.user_id,
            'username': worker.user.username,
            'stage': worker.stage,
            'stage_label': dict(ProductionTask.STATION_CHOICES).get(worker.stage, worker.stage),
            'skills': worker.skills,
            'skill_priority': worker.skill_priority,
            'is_available': worker.is_available,
            'excluded_products_count': worker.excluded_products.count(),
            'excluded_items_count': 0,
        })

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            worker.user_id = data.get('user_id', worker.user_id)
            worker.stage = data.get('stage', worker.stage)
            worker.is_available = data.get('is_available', worker.is_available)
            worker.skills = data.get('skills', worker.skills)
            worker.skill_priority = data.get('skill_priority', data.get('skill_costs', worker.skill_priority))
            worker.save()
            return JsonResponse({'success': True, 'worker': worker_to_dict(worker)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'DELETE':
        worker.delete()
        return JsonResponse({'success': True})


@login_required
@admin_or_manager_required
def painting_worker_exclusion_api(request, worker_id):
    worker = get_object_or_404(WorkerProfile, pk=worker_id, stage='paint')

    if request.method == 'GET':
        items = []
        if 'products' in request.path:
            items = [{'id': p.id, 'text': p.name} for p in worker.excluded_products.all()]
        else:
            items = [{'id': i.id, 'text': f"{i.order.id} - {i.product.name}"} for i in worker.excluded_items.all()]
        return JsonResponse({'success': True, 'items': items})

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            item_ids = data.get('items', [])
            valid_ids = [int(i) for i in item_ids if str(i).isdigit()]
            if 'products' in request.path:
                worker.excluded_products.set(valid_ids)
            else:
                worker.excluded_items.set(valid_ids)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@login_required
@admin_or_manager_required
def search_products_api(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.select_related('category')
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(category__name__icontains=q)
        )[:20]
    else:
        products = products.all()[:20]
    results = [{
        'id': p.id,
        'text': f"{p.category.name} - {p.name}"
    } for p in products]
    return JsonResponse({'results': results})


@login_required
@admin_or_manager_required
def search_items_api(request):
    q = request.GET.get('q', '')
    items = OrderItem.objects.select_related('order', 'product').filter(
        Q(order__id__icontains=q) | Q(product__name__icontains=q)
    )[:20]
    results = [{'id': i.id, 'text': f"#{i.order.id} - {i.product.name}"} for i in items]
    return JsonResponse({'results': results})


# ============================================================
# Admin Order Management Views
# ============================================================

@login_required
@admin_or_manager_required
def admin_edit_order_item(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)
    order = item.order
    existing_colors = {c.part: c.code for c in item.ordercolor.all()}

    if request.method == 'POST':
        item_form = EditOrderItemForm(request.POST, instance=item)
        color_form = ColorSelectionForm(request.POST)

        if item_form.is_valid() and color_form.is_valid():
            with transaction.atomic():
                updated_item = item_form.save(commit=False)
                if 'product' in item_form.changed_data:
                    updated_item.unit_price = updated_item.product.base_price
                updated_item.save()

                item.ordercolor.all().delete()
                for part_value, _ in OrderColor.PART_CHOICES:
                    code = color_form.cleaned_data.get(f'color_{part_value}')
                    if code:
                        OrderColor.objects.create(part=part_value, code=code, orderitem=item)

                messages.success(request, 'آیتم با موفقیت ویرایش شد.')
                return redirect('production:admin_edit_order', order_id=order.id)
        else:
            messages.error(request, 'خطا در ویرایش آیتم.')
    else:
        item_form = EditOrderItemForm(instance=item)
        color_form = ColorSelectionForm(initial={
            f'color_{part}': existing_colors.get(part, '')
            for part, _ in OrderColor.PART_CHOICES
        })

    context = {
        'item_form': item_form,
        'color_form': color_form,
        'item': item,
        'order': order,
    }
    return render(request, 'production/admin_edit_order_item.html', context)


@login_required
@admin_or_manager_required
def admin_edit_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات سفارش به‌روز شد.')
            return redirect('production:admin_edit_order', order_id=order.id)
        else:
            messages.error(request, 'خطا در ویرایش اطلاعات سفارش.')
    else:
        form = OrderEditForm(instance=order)

    items = order.items.select_related('product__category').prefetch_related('ordercolor')
    item_form = OrderItemForm()
    color_form = ColorSelectionForm()

    context = {
        'order': order,
        'form': form,
        'items': items,
        'item_form': item_form,
        'color_form': color_form,
        'station_choices': ProductionTask.STATION_CHOICES,
        'has_any_tasks': order.tasks.exists(),
        'has_paint_tasks': order.tasks.filter(station_name='paint').exists(),
    }
    return render(request, 'production/admin_order_edit.html', context)


@login_required
@admin_or_manager_required
def admin_delete_order_item(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)
    order_id = item.order.id
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'آیتم حذف شد.')
    else:
        messages.warning(request, 'درخواست غیرمجاز.')
    return redirect('production:admin_edit_order', order_id=order_id)


@login_required
@admin_or_manager_required
def admin_add_order_item(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        item_form = OrderItemForm(request.POST)
        color_form = ColorSelectionForm(request.POST)
        if item_form.is_valid() and color_form.is_valid():
            with transaction.atomic():
                product = item_form.cleaned_data['product']
                order_item = item_form.save(commit=False)
                order_item.order = order
                order_item.product = product
                order_item.unit_price = product.base_price
                order_item.save()

                for part_value, _ in OrderColor.PART_CHOICES:
                    code = color_form.cleaned_data.get(f'color_{part_value}')
                    if code:
                        OrderColor.objects.create(part=part_value, code=code, orderitem=order_item)
                messages.success(request, f'آیتم "{product.name}" اضافه شد.')
                return redirect('production:admin_edit_order', order_id=order.id)
        else:
            messages.error(request, 'خطا در افزودن آیتم.')
    return redirect('production:admin_edit_order', order_id=order_id)


@login_required
@admin_or_manager_required
def admin_delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'سفارش {order_id} با موفقیت حذف شد.')
        return redirect('production:order_list')
    else:
        messages.warning(request, 'درخواست غیرمجاز.')
        return redirect('production:admin_edit_order', order_id=order_id)


@login_required
@admin_or_manager_required
def admin_order_tasks(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    tasks = order.tasks.select_related('part', 'assigned_worker', 'painting_stage').order_by('step_order')

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        if task_id and new_status in ['waiting', 'pending', 'done']:
            task = get_object_or_404(ProductionTask, pk=task_id, order=order)
            task.status = new_status
            task.save()
            messages.success(request, f'وضعیت تسک {task.id} به {task.get_status_display()} تغییر یافت.')
        return redirect('production:admin_order_tasks', order_id=order.id)

    context = {
        'order': order,
        'tasks': tasks,
    }
    return render(request, 'production/admin_order_tasks.html', context)


@login_required
@admin_or_manager_required
def admin_delete_task(request, task_id):
    task = get_object_or_404(ProductionTask, pk=task_id)
    order_id = task.order.id
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'تسک با موفقیت حذف شد.')
    return redirect('production:admin_order_tasks', order_id=order_id)


@login_required
@admin_or_manager_required
def admin_tasks_management(request):
    tasks = ProductionTask.objects.select_related(
        'order', 'part', 'order_item', 'assigned_worker', 'painting_stage'
    ).order_by('order__id', 'step_order')

    search_query = request.GET.get('q', '')
    station_filter = request.GET.get('station', '')
    status_filter = request.GET.get('status', '')
    unit_filter = request.GET.get('unit', '')
    order_filter = request.GET.get('order', '')

    if search_query:
        tasks = tasks.filter(
            Q(order__number__icontains=search_query) |
            Q(order__customer__name__icontains=search_query) |
            Q(part__name__icontains=search_query) |
            Q(order_item__product__name__icontains=search_query)
        )
    if station_filter:
        tasks = tasks.filter(station_name=station_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if order_filter:
        tasks = tasks.filter(order_id=order_filter)
    if unit_filter:
        tasks = tasks.filter(order_item_id=unit_filter)

    unit_qs = tasks.filter(order_item__isnull=False).values(
        'order_id', 'order_item_id'
    ).distinct().order_by('order_id', 'order_item_id')

    if request.method == 'POST':
        action = request.POST.get('action')
        task_ids = request.POST.getlist('task_ids')

        if action == 'fix_chain':
            if task_ids:
                orders = Order.objects.filter(tasks__id__in=task_ids).distinct()
            else:
                orders = Order.objects.filter(tasks__in=tasks).distinct()
            fixed = 0
            for order in orders:
                order_tasks = order.tasks.order_by('step_order')
                for task in order_tasks:
                    if task.status == 'done':
                        if task.station_name == 'paint' and task.order_item_id:
                            next_task = order.tasks.filter(
                                station_name='paint',
                                order_item=task.order_item,
                                color_part=task.color_part,
                                step_order=task.step_order + 1,
                            ).first()
                        else:
                            next_task = order.tasks.filter(
                                part=task.part,
                                step_order=task.step_order + 1,
                            ).first()
                        if next_task and next_task.status == 'waiting':
                            next_task.status = 'pending'
                            next_task.save(update_fields=['status'])
                            fixed += 1
            messages.success(request, f'تعداد {fixed} وظیفه بعدی فعال شد.')
        elif action == 'bulk_status':
            new_status = request.POST.get('bulk_status')
            qs = ProductionTask.objects.filter(id__in=task_ids)
            if new_status in dict(ProductionTask.TASK_STATUS):
                count = qs.count()
                for task in qs:
                    task.status = new_status
                    old = ProductionTask.objects.filter(pk=task.pk).values_list('status', flat=True).first()
                    if new_status == 'done' and old != 'done':
                        task.completed_at = jdatetime.date.today()
                    task.save(update_fields=['status', 'completed_at'])
                messages.success(request, f'وضعیت {count} وظیفه تغییر یافت.')
        elif action == 'bulk_worker':
            worker_id = request.POST.get('bulk_worker')
            if worker_id:
                count = ProductionTask.objects.filter(id__in=task_ids).count()
                ProductionTask.objects.filter(id__in=task_ids).update(assigned_worker_id=worker_id)
                messages.success(request, f'کارگر برای {count} وظیفه تخصیص داده شد.')
        elif action == 'bulk_delete':
            count = ProductionTask.objects.filter(id__in=task_ids).count()
            ProductionTask.objects.filter(id__in=task_ids).delete()
            messages.success(request, f'تعداد {count} وظیفه حذف شد.')

        return redirect('production:admin_tasks_management')

    orders = Order.objects.all().order_by('-id')[:100]
    users = User.objects.filter(is_superuser=False).order_by('username')

    context = {
        'tasks': tasks,
        'station_choices': ProductionTask.STATION_CHOICES,
        'task_status_choices': ProductionTask.TASK_STATUS,
        'search_query': search_query,
        'station_filter': station_filter,
        'status_filter': status_filter,
        'unit_filter': unit_filter,
        'order_filter': order_filter,
        'orders': orders,
        'units': unit_qs,
        'users': users,
    }
    return render(request, 'production/admin_tasks_management.html', context)


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
        context['total_completed_today'] = sum(row['total_tasks'] for row in context['report'])
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stations'] = ProductionTask.STATION_CHOICES
        context['status_choices'] = ProductionTask.TASK_STATUS
        return context


class WorkerListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = WorkerProfile
    template_name = 'production/worker_list.html'
    context_object_name = 'workers'
    login_url = 'accounts:login'

    def test_func(self):
        return is_production_staff(self.request.user)

    def get_queryset(self):
        return WorkerProfile.objects.select_related('user').order_by('user__username')


class HolidayListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Holiday
    template_name = 'production/holiday_list.html'
    context_object_name = 'holidays'
    login_url = 'accounts:login'

    def test_func(self):
        return is_production_staff(self.request.user)

    def get_queryset(self):
        return Holiday.objects.order_by('date')


class PaintingProcessListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PaintingProcess
    template_name = 'production/painting_process_list.html'
    context_object_name = 'processes'
    login_url = 'accounts:login'

    def test_func(self):
        return is_production_staff(self.request.user)

    def get_queryset(self):
        return PaintingProcess.objects.order_by('name')


# ============================================================
# Painting Holidays
# ============================================================

@login_required
@admin_or_manager_required
def painting_holidays_view(request):
    holidays = Holiday.objects.all().order_by('date')
    context = {'holidays': holidays}
    return render(request, 'production/painting_management/holidays.html', context)


# === MIGRATED VIEWS START ===


@login_required
@staff_or_representative_required
@require_POST
def order_generate_tasks(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.generate_tasks():
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'تسک‌ها قبلاً ایجاد شده‌اند.'})


@login_required
@admin_or_manager_required
def dashboard(request):
    total_orders = Order.objects.count()
    active_orders = Order.objects.filter(status__in=['draft', 'planned', 'producing']).count()
    completed_orders = Order.objects.filter(status='completed').count()
    producing_orders = Order.objects.filter(status='producing').count()

    today_shamsi = jdatetime.date.today()
    today_gregorian = today_shamsi.togregorian()
    shipped_today = PackagingUnit.objects.filter(
        is_shipped=True,
        shipped_at__date=today_gregorian
    ).count()

    station_load = []
    for code, name in ProductionTask.STATION_CHOICES:
        pending = ProductionTask.objects.filter(station_name=code, status='pending').count()
        waiting = ProductionTask.objects.filter(station_name=code, status='waiting').count()
        station_load.append({
            'name': name,
            'pending': pending,
            'waiting': waiting,
            'total': pending + waiting,
        })

    latest_orders = Order.objects.select_related('customer', 'user').order_by('-id')[:5]

    context = {
        'total_orders': total_orders,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'producing_orders': producing_orders,
        'shipped_today': shipped_today,
        'station_load': station_load,
        'latest_orders': latest_orders,
        'today_shamsi': today_shamsi,
    }
    return render(request, 'production/dashboard.html', context)


@login_required
@staff_or_representative_required
def order_list(request):
    orders = Order.objects.select_related('customer').all().order_by('-id')

    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    q = request.GET.get('q')
    if q:
        orders = orders.filter(
            Q(id__icontains=q) |
            Q(customer__name__icontains=q) |
            Q(user__username__icontains=q) |
            Q(number__icontains=q)
        )

    id_filter = request.GET.get('id_filter')
    if id_filter:
        orders = orders.filter(id__icontains=id_filter)

    customer_filter = request.GET.get('customer_filter')
    if customer_filter:
        orders = orders.filter(customer__name__icontains=customer_filter)

    paginator = Paginator(orders, 200)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'status_filter': status,
        'search_query': q,
        'id_filter': id_filter,
        'customer_filter': customer_filter,
    }
    return render(request, 'production/order_list.html', context)


@login_required
@staff_or_representative_required
def order_item_list(request):
    items = OrderItem.objects.select_related(
        'order__user', 'product__category'
    ).prefetch_related(
        'logs', 'ordercolor'
    ).order_by('-order__created_at')

    q = request.GET.get('q')
    if q:
        items = items.filter(
            Q(order__id__icontains=q) |
            Q(id__icontains=q) |
            Q(order__customer__user__username__icontains=q) |
            Q(product__name__icontains=q) |
            Q(product__category__name__icontains=q)
        )

    customer_id = request.GET.get('customer')
    if customer_id:
        items = items.filter(order__customer__user_id=customer_id)

    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(product__category_id=category_id)

    product_id = request.GET.get('product')
    if product_id:
        items = items.filter(product_id=product_id)

    sort = request.GET.get('sort', '-id')
    items = items.order_by(sort)

    paginator = Paginator(items, 200)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for item in page_obj:
        stage_dates = {}
        for log in item.logs.all():
            if log.created_at:
                jdate = log.created_at
                stage_dates[log.stage] = f"{jdate.month:02d}/{jdate.day:02d}"
        item.stage_dates = stage_dates
        item.color = item.color_summary

    customers = User.objects.all()
    categories = ProductCategory.objects.all()

    if category_id:
        products = Product.objects.filter(category_id=category_id).order_by('name')
    else:
        products = Product.objects.none()

    context = {
        'items': page_obj,
        'station_choices': ProductionTask.STATION_CHOICES,
        'search_query': q,
        'customers': customers,
        'categories': categories,
        'products': products,
        'selected_customer': customer_id,
        'selected_category': category_id,
        'selected_product': product_id,
        'sort': sort,
    }
    return render(request, 'production/order_item.html', context)


@login_required
@staff_or_representative_required
def item_detail(request, pk):
    item = get_object_or_404(
        OrderItem.objects.select_related('product', 'order__customer').prefetch_related('logs'),
        pk=pk
    )

    stage_status_list = []
    for code, name in ProductionTask.STATION_CHOICES:
        log = item.logs.filter(stage=code).first()
        if log and log.created_at:
            jdate = log.created_at
            stage_status_list.append(f"{jdate.month:02d}/{jdate.day:02d}")
        else:
            stage_status_list.append(None)

    all_tasks = ProductionTask.objects.filter(order=item.order).select_related('part')

    task_map = {}
    for task in all_tasks:
        if not task.part:
            continue
        task_map[(task.part_id, task.station_name)] = task.status
        if task.part.base_part_id:
            task_map[(task.part.base_part_id, task.station_name)] = task.status

    bom_parts = []
    for bom_entry in item.product.bom.select_related('part').all():
        part = bom_entry.part
        station_status = {}
        for code, name in ProductionTask.STATION_CHOICES:
            status = task_map.get((part.id, code))
            station_status[code] = status
        bom_parts.append({
            'part': part,
            'quantity': bom_entry.quantity,
            'station_status': station_status,
        })

    context = {
        'item': item,
        'stage_status_list': stage_status_list,
        'station_choices': ProductionTask.STATION_CHOICES,
        'bom_parts': bom_parts,
        'has_paint_tasks': item.paint_tasks.exists(),
    }
    return render(request, 'production/item.html', context)


@login_required
@staff_or_representative_required
def scan_qr(request, pk):
    item = get_object_or_404(OrderItem.objects.select_related('order'), pk=pk)

    if not hasattr(request.user, 'worker_profile'):
        messages.error(request, "پروفایل کاری ندارید")
        return redirect('item_detail', pk=pk)

    stage = request.user.worker_profile.stage

    if ProductionLog.objects.filter(order_item=item, stage=stage).exists():
        messages.warning(request, "قبلاً ثبت شده")
        return redirect('item_detail', pk=pk)

    ProductionLog.objects.create(
        order_item=item,
        stage=stage,
        user=request.user
    )

    task = ProductionTask.objects.filter(
        order=item.order,
        station_name=stage,
        status='pending'
    ).first()

    if not task:
        messages.error(request, "مرحله مجاز نیست")
        return redirect('item_detail', pk=pk)

    task.status = 'done'
    task.scanned_by = request.user
    task.save()

    messages.success(request, "مرحله ثبت شد ✅")
    return redirect('item_detail', pk=pk)


@login_required
@admin_or_manager_required
def print_sheet(request, pk):
    item = get_object_or_404(
        OrderItem.objects.select_related('order__customer', 'product__category'),
        pk=pk
    )
    item.color = item.color_summary
    bom_list = item.product.bom.select_related('part').all()
    item.bompart = [{'part': b.part, 'quantity': b.quantity} for b in bom_list]
    return render(request, 'production/print.html', {'item': item})


@login_required
@admin_or_manager_required
def print_lable(request, pk):
    item = get_object_or_404(OrderItem.objects.select_related('order__customer', 'product__category'), pk=pk)
    item.color = item.color_summary
    return render(request, 'production/print_lable.html', {'item': item})


@login_required
@admin_or_manager_required
def order_print(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product__category', 'items__ordercolor'),
        id=order_id
    )
    items_data = []
    for item in order.items.all():
        items_data.append({
            'id': item.id,
            'product': item.product.name,
            'category': item.product.category.name,
            'quantity': item.quantity,
            'size': item.size,
            'colors': item.color_summary,
            'notes': item.notes
        })
    return render(request, 'production/order_print.html', {
        'order': order,
        'items': items_data,
        'customer': order.customer.name if order.customer else ''
    })


# === CHUNK 1 END ===


@login_required
@staff_or_representative_required
def export_autocut_xml(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    cut_tasks = ProductionTask.objects.filter(
        order=order,
        station_name='cut',
        status='pending'
    ).select_related('part', 'part__material')

    tasks_by_material = {}
    for task in cut_tasks:
        material = task.part.material
        if material not in tasks_by_material:
            tasks_by_material[material] = []
        tasks_by_material[material].append(task)

    NS = "http://www.King-stone.com"
    ET.register_namespace('', NS)
    root = ET.Element(f"{{{NS}}}AutoCUT", {"ver": "500"})

    project = ET.SubElement(root, f"{{{NS}}}Project", {
        "Name": "Project",
        "Selected": "0",
        "Update": "0",
        "DefaultLevel": "0",
        "UserFields": "F2,F3,F4,F5,F26,F18,F19,F20,",
        "FieldLabels": "TLGrain=دسته محصول,TLOrder=نام محصول,TLType=fcfffff,F2=نام قطعه,F3=بارکد,F4=نوار طول 1,F5=نوار طول 2,F26=نوار عرض1,F18=نوار عرض 2,F19=تحویل به,F20=نام مشتری,"
    })

    for material, tasks in tasks_by_material.items():
        material_type = material.name.replace(' ', '-')

        data = ET.SubElement(project, f"{{{NS}}}Data", {
            "Class": "3",
            "TotalUnit": "1000000",
            "Type": material_type,
            "Ply": str(material.thickness)
        })

        objective = ET.SubElement(data, f"{{{NS}}}Objective", {"Type": "Shape", "Count": str(len(tasks))})

        for idx, task in enumerate(tasks, start=1):
            part = task.part
            order_item = order.items.filter(product__bom__part=part).first()
            product_name = order_item.product.name if order_item else ""
            product_category = order_item.product.category if order_item else ""
            customer_name = order.user.username if order.user.username else ""

            shape = ET.SubElement(objective, f"{{{NS}}}Shape", {
                "Name": f"P{idx:03d}",
                "X": str(part.length),
                "Y": str(part.width),
                "Turn": "true" if part.turn else "false",
                "Grain": product_category or "",
                "Order": product_name,
                "Count": str(task.quantity),
                "F2": part.f2 or part.name,
                "F3": part.f3 or "",
                "F4": part.f4 or "",
                "F5": part.f5 or "",
                "F26": part.f26 or "",
                "F18": part.f18 or "",
                "F19": part.routing_code or "",
                "F20": customer_name or "",
            })

    xml_str = ET.tostring(root, encoding='utf-16', method='xml')
    response = HttpResponse(xml_str, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}_autocut.xml"'
    return response


@login_required
@staff_or_representative_required
def export_multiple_autocut(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    order_ids = request.POST.getlist('order_ids')
    if not order_ids:
        messages.error(request, "هیچ سفارشی انتخاب نشده است.")
        return redirect('order_list')

    orders = get_list_or_404(Order, pk__in=order_ids)

    cut_tasks = ProductionTask.objects.filter(
        order__in=orders,
        station_name='cut',
        status='pending'
    ).select_related('part', 'part__material', 'order', 'order__customer')

    if not cut_tasks.exists():
        messages.warning(request, "هیچ قطعه‌ای در انتظار برش برای سفارشات انتخاب‌شده یافت نشد.")
        return redirect('order_list')

    tasks_by_material = {}
    for task in cut_tasks:
        material = task.part.material
        if material not in tasks_by_material:
            tasks_by_material[material] = []
        if task not in tasks_by_material[material]:
            tasks_by_material[material].append(task)

    NS = "http://www.King-stone.com"
    ET.register_namespace('', NS)
    root = ET.Element(f"{{{NS}}}AutoCUT", {"ver": "500"})

    project = ET.SubElement(root, f"{{{NS}}}Project", {
        "Name": "MultipleOrders",
        "Selected": "0",
        "Update": "0",
        "DefaultLevel": "0",
        "UserFields": "F2,F3,F4,F5,F26,F18,F19,F20,",
        "FieldLabels": "TLGrain=دسته محصول,TLOrder=نام محصول,TLType=fcfffff,F2=نام قطعه,F3=بارکد,F4=نوار طول 1,F5=نوار طول 2,F26=نوار عرض1,F18=نوار عرض 2,F19=تحویل به,F20=نام مشتری,"
    })

    shape_counter = 1
    for material, tasks in tasks_by_material.items():
        material_type = material.name.replace(' ', '-')
        data = ET.SubElement(project, f"{{{NS}}}Data", {
            "Class": "3",
            "TotalUnit": "1000000",
            "Type": material_type,
            "Ply": str(material.thickness)
        })

        objective = ET.SubElement(data, f"{{{NS}}}Objective", {
            "Type": "Shape",
            "Count": str(len(tasks))
        })

        for task in tasks:
            part = task.part
            order = task.order
            order_item = order.items.filter(product__bom__part=part).first()
            product_name = order_item.pname if order_item else ""
            product_category = order_item.grain if order_item else ""
            customer_name = order.user.username if order.user.username else ""

            shape = ET.SubElement(objective, f"{{{NS}}}Shape", {
                "Name": f"P{shape_counter:03d}",
                "X": str(part.length),
                "Y": str(part.width),
                "Turn": "true" if part.turn else "false",
                "Grain": part.grain or product_category or "",
                "Order": part.pname,
                "Count": str(task.quantity),
                "F2": part.f2 or part.name,
                "F3": part.f3 or "",
                "F4": part.f4 or "",
                "F5": part.f5 or "",
                "F26": part.f26 or "",
                "F18": part.f18 or "",
                "F19": part.routing_code or "",
                "F20": customer_name or "",
            })
            shape_counter += 1

    xml_str = ET.tostring(root, encoding='utf-16', method='xml')

    with transaction.atomic():
        updated_count = 0
        for task in cut_tasks:
            task.status = 'done'
            task.scanned_by = request.user
            task.save()
            updated_count += 1

    messages.success(
        request,
        f"فایل برش با موفقیت ایجاد و {updated_count} قطعه به‌عنوان انجام‌شده ثبت گردید. "
        "مراحل بعدی به‌طور خودکار فعال شدند."
    )

    response = HttpResponse(xml_str, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="batch_autocut.xml"'
    return response


@login_required
@admin_or_manager_required
def upload_form(request):
    if request.method == 'POST':
        file = request.FILES.get('excel_file')
        if not file:
            messages.error(request, "فایلی انتخاب نشده است.")
            return redirect('upload_form')

        try:
            df = pd.read_excel(file)
        except Exception as e:
            messages.error(request, f"خطا در خواندن فایل: {e}")
            return redirect('upload_form')

        saved = 0
        for idx, row in df.iterrows():
            try:
                with transaction.atomic():
                    username = str(row.get('نام', '')).strip()
                    if not username:
                        username = f"user_{idx}"
                    user, _ = User.objects.get_or_create(username=username)

                    customer_name = str(row.get('مشتری', '')).strip()
                    if not customer_name:
                        customer_name = f"{idx}"
                    customer, _ = Customer.objects.get_or_create(
                        user=user,
                        name=customer_name
                    )
                    order_id = int(row.get('شماره'))
                    order, _ = Order.objects.get_or_create(
                        id=order_id,
                        defaults={'user': user, 'customer': customer}
                    )
                    category, _ = ProductCategory.objects.get_or_create(name=str(row.get('گروه محصول', '')).strip())
                    size_val = str(row.get('اندازه', ''))
                    if size_val in ['nan', 'استاندارد']:
                        size_val = ''
                    product, _ = Product.objects.get_or_create(
                        category=category,
                        name=str(row.get('محصول', '')).strip(),
                    )
                    order_item = OrderItem.objects.create(
                        order=order,
                        id=idx + 1,
                        product=product,
                        quantity=int(row.get('تعداد', 1)),
                        size=size_val,
                        notes=str(row.get('توضیحات', ''))
                    )

                    color_parts = ['بدنه', 'درب', 'دستگیره', 'پایه', 'صفحه']
                    for part in color_parts:
                        code = str(row.get(part, 'nan'))
                        if code and code != 'nan':
                            OrderColor.objects.create(
                                part=part,
                                code=code.split('.')[0],
                                orderitem=order_item
                            )
                    saved += 1
            except Exception as e:
                logger.exception(f"خطا در ردیف {idx}: {e}")
                messages.error(request, f"خطا در ردیف {idx + 1}: {e}")
        messages.success(request, f'{saved} سفارش با موفقیت ذخیره شد.')
        return redirect('upload_form')

    return render(request, 'production/upload.html')


@login_required
@admin_or_manager_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            messages.success(request, f'سفارش #{order.id} ایجاد شد.')
            return redirect('add_item', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'production/create_order.html', {'form': form})


@login_required
@admin_or_manager_required
def add_item(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.save()
            messages.success(request, 'آیتم اضافه شد.')
            return redirect('add_colors', item_id=item.id)
    else:
        form = OrderItemForm()
    return render(request, 'production/orders/add_item.html', {'form': form, 'order': order})


@login_required
@admin_or_manager_required
def add_colors(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    if request.method == 'POST':
        parts = ['بدنه', 'درب', 'پایه', 'دستگیره', 'صفحه']
        for part in parts:
            form = ColorForm(request.POST, prefix=part)
            if form.is_valid():
                color = form.save(commit=False)
                color.orderitem = item
                color.part = part
                color.save()
        messages.success(request, 'رنگ‌ها ثبت شد.')
        return redirect('order_list')
    else:
        color_forms = [ColorForm(prefix=p) for p in ['بدنه', 'درب', 'پایه', 'دستگیره', 'صفحه']]
    return render(request, 'production/orders/add_colors.html', {'item': item, 'color_forms': color_forms})


@login_required
@admin_or_manager_required
def create_complete_order(request):
    if request.method == 'POST':
        form = CompleteOrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                customer, _ = Customer.objects.get_or_create(name=form.cleaned_data['customer_name'])
                category, _ = ProductCategory.objects.get_or_create(name=form.cleaned_data['category_name'])
                product = Product.objects.create(
                    category=category,
                    name=form.cleaned_data['product_name'],
                    size=form.cleaned_data['size']
                )
                order = Order.objects.create(user=request.user, customer=customer)
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=form.cleaned_data['quantity'],
                    notes=form.cleaned_data['notes'],
                    size=form.cleaned_data['size']
                )
                colors_data = [
                    ('بدنه', form.cleaned_data['rang_bazne']),
                    ('درب', form.cleaned_data['rang_darb']),
                    ('پایه', form.cleaned_data['rang_paye']),
                    ('دستگیره', form.cleaned_data['rang_dastgire']),
                ]
                for part, code in colors_data:
                    if code:
                        OrderColor.objects.create(part=part, code=code, orderitem=order_item)
            messages.success(request, f'سفارش #{order.id} کامل ایجاد شد.')
            return redirect('order_list')
    else:
        form = CompleteOrderForm()
    return render(request, 'production/create_complete.html', {'form': form})


# === CHUNK 2 END ===


@login_required
@staff_or_representative_required
def scan_part(request):
    if not hasattr(request.user, 'worker_profile'):
        messages.error(request, "")
        return redirect('dashboard')

    worker_stage = request.user.worker_profile.stage
    pending_tasks = ProductionTask.objects.filter(
        station_name=worker_stage,
        status='pending'
    ).select_related('part', 'order').order_by('order__created_at')

    if request.method == 'POST':
        barcode = request.POST.get('barcode', '').strip()
        task_id = request.POST.get('task_id')

        if task_id:
            task = get_object_or_404(pending_tasks, id=task_id)
            with transaction.atomic():
                task.status = 'done'
                task.scanned_by = request.user
                task.save()

            if worker_stage == 'cnc':
                file_barcode = re.sub(r'\.item\d+$', '', task.part.f3)
                download_url = reverse('download_cnc_file', args=[file_barcode])
                messages.success(request, f"تسک '{task.part.name}' تکمیل شد. دریافت فایل...")
                return redirect(download_url)

            if worker_stage == 'dr':
                file_barcode = re.sub(r'\.item\d+$', '', task.part.f3)
                download_url = reverse('download_dr_file', args=[file_barcode])
                messages.success(request, f" '{task.part.name}' تکمیل شد. دریافت فایل سوراخکاری...")
                return redirect(download_url)

            messages.success(request, f" قطعه '{task.part.name}' با موفقیت تکمیل شد.")
            return redirect('scan_part')

        if barcode and worker_stage == 'cnc':
            clean_barcode = re.sub(r'\.cnc$', '', barcode, flags=re.IGNORECASE)
            try:
                part = Part.objects.get(f3=clean_barcode)
            except Part.DoesNotExist:
                messages.error(request, f"قطعه‌ای با بارکد '{barcode}' یافت نشد.")
                return redirect('scan_part')

            task = pending_tasks.filter(part=part).first()
            if not task:
                messages.error(request, f"هیچ  در انتظاری برای قطعه '{part.name}' در ایستگاه شما یافت نشد.")
                return redirect('scan_part')

            with transaction.atomic():
                task.status = 'done'
                task.scanned_by = request.user
                task.save()

            messages.success(request, f"قطعه '{part.name}' (بارکد: {barcode}) تکمیل شد.")
            return redirect('scan_part')

        messages.error(request, "لطفاً بارکد را وارد کنید یا یکی از قطعه را انتخاب نمایید.")
        return redirect('scan_part')

    stage_display = dict(ProductionTask.STATION_CHOICES).get(worker_stage, worker_stage)
    context = {
        'pending_tasks': pending_tasks,
        'worker_stage': worker_stage,
        'stage_display': stage_display,
    }
    return render(request, 'production/scan_part.html', context)


@login_required
@staff_or_representative_required
def scan_part_cnc(request):
    if request.method != 'POST':
        return redirect('scan_part')

    barcode = request.POST.get('barcode', '').strip()
    if not barcode:
        messages.error(request, "لطفاً بارکد قطعه را وارد کنید.")
        return redirect('scan_part')

    clean_barcode = re.sub(r'\.cnc$', '', barcode, flags=re.IGNORECASE)
    part = Part.objects.filter(f3=clean_barcode).first()
    if not part:
        messages.error(request, f"قطعه‌ای با بارکد '{barcode}' یافت نشد.")
        return redirect('scan_part')

    if not hasattr(request.user, 'worker_profile'):
        messages.error(request, "پروفایل کاری شما تعریف نشده است.")
        return redirect('dashboard')

    worker_stage = request.user.worker_profile.stage
    if worker_stage != 'cnc':
        messages.error(request, "شما مجاز به اسکن در ایستگاه CNC نیستید.")
        return redirect('dashboard')

    task = ProductionTask.objects.filter(
        part=part,
        station_name='cnc',
        status='pending'
    ).first()

    if not task:
        messages.error(request, f"هیچ  در انتظاری برای قطعه '{part.name}' در ایستگاه CNC یافت نشد.")
        return redirect('scan_part')

    with transaction.atomic():
        task.status = 'done'
        task.scanned_by = request.user
        task.save()

    source_dir = getattr(settings, 'CNC_SOURCE_DIR', '')
    extension = getattr(settings, 'CNC_FILE_EXTENSION', '.cnc')

    file_barcode = re.sub(r'\.item\d+$', '', part.f3)
    filename = f"{file_barcode}{extension}"
    file_path = os.path.join(source_dir, filename)

    if not os.path.exists(file_path):
        messages.warning(
            request,
            f"✅ تسک CNC تکمیل شد، اما فایل '{filename}' در سرور یافت نشد."
        )
        return redirect('scan_part')

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['X-CNC-Status'] = 'success'
        return response


@login_required
@staff_or_representative_required
def download_cnc_file(request, barcode):
    clean_barcode = re.sub(r'\.cnc$', '', barcode, flags=re.IGNORECASE)

    part = Part.objects.filter(f3__startswith=clean_barcode).first()
    if not part:
        raise Http404(f"قطعه‌ای با بارکد '{barcode}' یافت نشد.")

    file_barcode = re.sub(r'\.item\d+$', '', clean_barcode)
    source_dir = getattr(settings, 'CNC_SOURCE_DIR', '')
    extension = getattr(settings, 'CNC_FILE_EXTENSION', '.cnc')
    filename = f"{file_barcode}{extension}"
    file_path = os.path.join(source_dir, filename)

    if not os.path.exists(file_path):
        raise Http404(f"فایل CNC با نام '{filename}' یافت نشد.")

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@login_required
@staff_or_representative_required
def scan_part_dr(request):
    if request.method != 'POST':
        return redirect('scan_part')

    barcode = request.POST.get('barcode', '').strip()
    if not barcode:
        messages.error(request, "لطفاً بارکد قطعه را وارد کنید.")
        return redirect('scan_part')

    clean_barcode = re.sub(r'\.(scx)$', '', barcode, flags=re.IGNORECASE)
    part = Part.objects.filter(f3=clean_barcode).first()
    if not part:
        messages.error(request, f"قطعه‌ای با بارکد '{barcode}' یافت نشد.")
        return redirect('scan_part')

    if not hasattr(request.user, 'worker_profile'):
        messages.error(request, "پروفایل کاری شما تعریف نشده است.")
        return redirect('dashboard')

    worker_stage = request.user.worker_profile.stage
    if worker_stage != 'dr':
        messages.error(request, "شما مجاز به اسکن در ایستگاه سوراخکاری نیستید.")
        return redirect('dashboard')

    task = ProductionTask.objects.filter(
        part=part,
        station_name='dr',
        status='pending'
    ).first()

    if not task:
        messages.error(request, f"هیچ  در انتظاری برای قطعه '{part.name}' در ایستگاه سوراخکاری یافت نشد.")
        return redirect('scan_part')

    with transaction.atomic():
        task.status = 'done'
        task.scanned_by = request.user
        task.save()

    source_dir = getattr(settings, 'DR_SOURCE_DIR', '')
    extension = getattr(settings, 'DR_FILE_EXTENSION', '.scx')

    file_barcode = re.sub(r'\.item\d+$', '', part.f3)
    filename = f"{file_barcode}{extension}"
    file_path = os.path.join(source_dir, filename)

    if not os.path.exists(file_path):
        messages.warning(
            request,
            f"✅  سوراخکاری تکمیل شد، اما فایل '{filename}' در سرور یافت نشد."
        )
        return redirect('scan_part')

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['X-DR-Status'] = 'success'
        return response


@login_required
@staff_or_representative_required
def download_dr_file(request, barcode):
    clean_barcode = re.sub(r'\.(scx)$', '', barcode, flags=re.IGNORECASE)

    part = Part.objects.filter(f3__startswith=clean_barcode).first()
    if not part:
        raise Http404(f"قطعه‌ای با بارکد '{barcode}' یافت نشد.")

    file_barcode = re.sub(r'\.item\d+$', '', clean_barcode)
    source_dir = getattr(settings, 'DR_SOURCE_DIR', '')
    extension = getattr(settings, 'DR_FILE_EXTENSION', '.xml')
    filename = f"{file_barcode}{extension}"
    file_path = os.path.join(source_dir, filename)

    if not os.path.exists(file_path):
        raise Http404(f"فایل سوراخکاری با نام '{filename}' یافت نشد.")

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# === CHUNK 3 END ===


@login_required
@admin_or_manager_required
def report_orders(request):
    data = Order.objects.values('status').annotate(count=Count('id'))
    return render(request, 'production/reports/orders.html', {'data': data})


@login_required
@staff_or_representative_required
def report_stages(request):
    base_items = OrderItem.objects.select_related(
        'order__user', 'product__category'
    ).prefetch_related(
        'logs', 'packaging_units'
    )

    q = request.GET.get('q')
    if q:
        base_items = base_items.filter(
            Q(order__id__icontains=q) |
            Q(product__name__icontains=q) |
            Q(order__customer__name__icontains=q) |
            Q(order__user__username__icontains=q)
        )

    representative_id = request.GET.get('representative')
    if representative_id:
        base_items = base_items.filter(order__user_id=representative_id)

    category_id = request.GET.get('category')
    if category_id:
        base_items = base_items.filter(product__category_id=category_id)

    product_id = request.GET.get('product')
    if product_id:
        base_items = base_items.filter(product_id=product_id)

    date_from = request.GET.get('date_from')
    if date_from:
        base_items = base_items.filter(order__created_at__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        base_items = base_items.filter(order__created_at__lte=date_to)

    total = base_items.count()
    summary = {}
    for code, name in ProductionTask.STATION_CHOICES:
        done_count = base_items.filter(logs__stage=code).distinct().count()
        summary[code] = {'name': name, 'done': done_count, 'total': total}

    stage_pending = request.GET.get('stage_pending')
    stage_done = request.GET.get('stage_done')
    items = base_items
    if stage_pending and stage_pending in dict(ProductionTask.STATION_CHOICES):
        items = items.exclude(logs__stage=stage_pending)
    if stage_done and stage_done in dict(ProductionTask.STATION_CHOICES):
        items = items.filter(logs__stage=stage_done)

    packaging_status = request.GET.get('packaging_status')
    shipping_status = request.GET.get('shipping_status')

    pack_units = PackagingUnit.objects.filter(order_item=OuterRef('pk'))
    ship_units = PackagingUnit.objects.filter(order_item=OuterRef('pk'))

    items = items.annotate(
        total_units=Count('packaging_units'),
        packed_count=Subquery(
            pack_units.filter(is_packed=True).values('order_item')
            .annotate(cnt=Count('id')).values('cnt'),
            output_field=IntegerField()
        ),
        shipped_count=Subquery(
            ship_units.filter(is_shipped=True).values('order_item')
            .annotate(cnt=Count('id')).values('cnt'),
            output_field=IntegerField()
        ),
    )

    if packaging_status == 'done':
        items = items.filter(total_units__gt=0, packed_count__gte=F('total_units'))
    elif packaging_status == 'pending':
        items = items.filter(total_units__gt=0, packed_count__lt=F('total_units'))
    elif packaging_status == 'none':
        items = items.filter(total_units=0)

    if shipping_status == 'done':
        items = items.filter(total_units__gt=0, shipped_count__gte=F('total_units'))
    elif shipping_status == 'pending':
        items = items.filter(total_units__gt=0, shipped_count__lt=F('total_units'))
    elif shipping_status == 'none':
        items = items.filter(total_units=0)

    items = items.order_by('-id')
    report_data = []
    for item in items:
        stage_status = {}
        for code, name in ProductionTask.STATION_CHOICES:
            log = item.logs.filter(stage=code).first()
            if log and log.created_at:
                jdate = log.created_at
                stage_status[code] = f"{jdate.month:02d}/{jdate.day:02d}"
            else:
                stage_status[code] = None

        total_units = item.packaging_units.count()
        packed_units = item.packaging_units.filter(is_packed=True).count()
        shipped_units = item.packaging_units.filter(is_shipped=True).count()

        report_data.append({
            'item': item,
            'stage_status': stage_status,
            'total_units': total_units,
            'packed_units': packed_units,
            'shipped_units': shipped_units,
            'representative': item.order.user.get_full_name() or item.order.user.username,
            'category_name': item.product.category.name,
        })

    representatives = User.objects.filter(order__isnull=False).distinct().order_by('username')
    categories = ProductCategory.objects.all()
    if category_id:
        products = Product.objects.filter(category_id=category_id).order_by('name')
    else:
        products = Product.objects.none()

    context = {
        'report_data': report_data,
        'station_choices': ProductionTask.STATION_CHOICES,
        'summary': summary,
        'search_query': q,
        'representatives': representatives,
        'categories': categories,
        'products': products,
        'selected_representative': representative_id,
        'selected_category': category_id,
        'selected_product': product_id,
        'date_from': date_from,
        'date_to': date_to,
        'stage_pending': stage_pending,
        'stage_done': stage_done,
        'packaging_status': packaging_status or '',
        'shipping_status': shipping_status or '',
    }
    return render(request, 'production/reports/stages.html', context)


@login_required
@admin_or_manager_required
@staff_or_representative_required
def report_workers(request):
    data = ProductionLog.objects.values('user__username').annotate(count=Count('id'))
    return render(request, 'production/reports/workers.html', {'data': data})


@login_required
@admin_or_manager_required
@staff_or_representative_required
def delayed_orders(request):
    limit = timezone.now() - timedelta(days=3)
    orders = Order.objects.filter(created_at__lt=limit).exclude(status='completed')
    return render(request, 'production/reports/delayed.html', {'orders': orders})


@login_required
@admin_or_manager_required
def create_order_step1(request):
    form = OrderCustomerForm(user=request.user)
    if request.method == 'POST':
        form = OrderCustomerForm(request.POST, user=request.user)
        if form.is_valid():
            if form.is_admin and form.cleaned_data.get('representative'):
                representative = form.cleaned_data['representative']
            else:
                representative = request.user

            customer = form.cleaned_data['customer']
            if not customer:
                customer = Customer.objects.create(
                    user=representative,
                    name=form.cleaned_data['new_customer_name'],
                    phone=form.cleaned_data['new_customer_phone'],
                    address=form.cleaned_data['new_customer_address']
                )
            order = Order.objects.create(customer=customer, user=representative,
                                         number=form.cleaned_data.get('number', ''),
                                         status='draft')
            messages.success(request, f"سفارش شماره {order.id} برای مشتری {customer.name} (نماینده: {representative.username}) ایجاد شد.")
            return redirect('create_order_step2', order_id=order.id)
    return render(request, 'production/orders/create_step1.html', {'form': form, 'is_admin': form.is_admin})


@login_required
@staff_or_representative_required
def ajax_load_customers(request):
    user_id = request.GET.get('representative')
    if user_id:
        customers = Customer.objects.filter(user_id=user_id).order_by('name')
    else:
        customers = Customer.objects.none()
    data = [{'id': c.id, 'name': c.name} for c in customers]
    return JsonResponse(data, safe=False)


@login_required
@admin_or_manager_required
def create_order_step2(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    existing_items = order.items.select_related('product__category').prefetch_related('ordercolor')

    if request.method == 'POST':
        item_form = OrderItemForm(request.POST)
        color_form = ColorSelectionForm(request.POST)
        if item_form.is_valid() and color_form.is_valid():
            with transaction.atomic():
                product = item_form.cleaned_data['product']
                order_item = item_form.save(commit=False)
                order_item.order = order
                order_item.product = product
                order_item.unit_price = product.base_price
                order_item.save()

                for part_value, _ in OrderColor.PART_CHOICES:
                    code = color_form.cleaned_data.get(f'color_{part_value}')
                    if code:
                        OrderColor.objects.create(
                            part=part_value,
                            code=code,
                            orderitem=order_item
                        )
                messages.success(request, f"آیتم '{order_item.product.name}' به سفارش اضافه شد.")
                if 'add_another' in request.POST:
                    return redirect('create_order_step2', order_id=order.id)
                else:
                    return redirect('order_list')
        else:
            for field, errors in item_form.errors.items():
                for error in errors:
                    messages.error(request, f"خطا در {field}: {error}")
            for field, errors in color_form.errors.items():
                for error in errors:
                    messages.error(request, f"خطا در رنگ‌ها: {error}")
    else:
        item_form = OrderItemForm()
        color_form = ColorSelectionForm()

    context = {
        'order': order,
        'item_form': item_form,
        'color_form': color_form,
        'existing_items': existing_items,
    }
    return render(request, 'production/orders/create_step2.html', context)


@login_required
def ajax_load_products(request):
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id).order_by('name')
    else:
        products = Product.objects.none()
    data = [{'id': p.id, 'name': str(p)} for p in products]
    return JsonResponse(data, safe=False)


@login_required
@staff_or_representative_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items__product__category',
            'items__ordercolor',
            'items__logs'
        ),
        id=order_id
    )

    for item in order.items.all():
        log_stages = set(item.logs.values_list('stage', flat=True))
        item.stages = {stage: (stage in log_stages) for stage, _ in ProductionTask.STATION_CHOICES}

    context = {
        'order': order,
        'station_choices': ProductionTask.STATION_CHOICES,
        'has_any_tasks': order.tasks.exists(),
        'has_paint_tasks': order.tasks.filter(station_name='paint').exists(),
    }
    return render(request, 'production/orders/order_detail.html', context)


def ajax_load_product_colors(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    raw_value = product.default_colors

    if isinstance(raw_value, dict):
        defaults = raw_value
    elif isinstance(raw_value, str):
        try:
            defaults = json.loads(raw_value)
        except json.JSONDecodeError:
            try:
                defaults = ast.literal_eval(raw_value)
            except (ValueError, SyntaxError):
                logger.warning(f"Cannot parse default_colors for product {product_id}: {raw_value}")
                defaults = {}
        if not isinstance(defaults, dict):
            defaults = {}
    else:
        defaults = {}

    return JsonResponse({'defaults': defaults})


# === CHUNK 4 END ===


@login_required
@admin_or_manager_required
def product_bom_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    part_qs = Part.objects.filter(productbom__product=product).distinct()

    PartFormSet = modelformset_factory(
        Part,
        form=PartForm,
        extra=0,
        can_delete=False
    )

    BOMFormSet = inlineformset_factory(
        Product,
        ProductBOM,
        fields=[
            'part', 'quantity',
            'color_part', 'allow_material_override', 'color_material_map',
            'size_affected', 'size_adjustment_rule',
        ],
        widgets={
            'size_adjustment_rule': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'color_part': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'color_material_map': forms.HiddenInput(),
        },
        extra=0,
        can_delete=True,
    )

    if request.method == 'POST':
        part_formset = PartFormSet(request.POST, prefix='parts', queryset=part_qs)
        bom_formset = BOMFormSet(request.POST, prefix='bom', instance=product)

        if part_formset.is_valid() and bom_formset.is_valid():
            part_formset.save()
            bom_formset.save()
            messages.success(request, '✅ اطلاعات با موفقیت ذخیره شد.')
            return redirect('product_bom_edit', product_id=product.id)
        else:
            messages.error(request, '⚠️ خطا در ذخیره‌سازی. لطفاً فیلدها را بررسی کنید.')
            logger.error("Part formset errors: %s", part_formset.errors)
            logger.error("BOM formset errors: %s", bom_formset.errors)
    else:
        part_formset = PartFormSet(prefix='parts', queryset=part_qs)
        bom_formset = BOMFormSet(prefix='bom', instance=product)

    context = {
        'product': product,
        'part_formset': part_formset,
        'bom_formset': bom_formset,
    }
    return render(request, 'production/product_bom_edit.html', context)


@login_required
@admin_or_manager_required
def admin_product_list(request):
    products = Product.objects.select_related('category').all()
    categories = ProductCategory.objects.all()

    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': q,
    }
    return render(request, 'production/admin_product_list.html', context)


# -------------------------------------------------------------------
# خروجی / ورودی اکسل
# -------------------------------------------------------------------

MODEL_ORDER = [
    'ProductCategory',
    'Material',
    'Customer',
    'WorkerProfile',
    'Product',
    'Part',
    'ProductBOM',
    'Order',
    'OrderItem',
    'Color',
    'ProductionTask',
    'ProductionLog',
    'PackagingUnit',
]


def get_model_by_name(name):
    for model in apps.get_app_config('catalog').get_models():
        if model.__name__ == name:
            return model
    return None


def _gregorian_to_shamsi_str(g_date, is_datetime=False):
    if isinstance(g_date, jdatetime.datetime):
        g_date = g_date.togregorian()
    if isinstance(g_date, jdatetime.date):
        g_date = g_date.togregorian()
    if isinstance(g_date, dt.datetime):
        return g_date.strftime('%Y-%m-%d %H:%M:%S') if is_datetime else g_date.strftime('%Y-%m-%d')
    if isinstance(g_date, dt.date):
        return g_date.strftime('%Y-%m-%d')
    return str(g_date)


def convert_dates_for_import(model, data):
    for field in model._meta.get_fields():
        if isinstance(field, (models.DateField, models.DateTimeField)):
            col = field.name
            if col not in data:
                continue

            val = data[col]
            is_datetime = isinstance(field, models.DateTimeField)

            if val is None or (isinstance(val, float) and math.isnan(val)):
                if is_datetime:
                    data[col] = dt.datetime.now()
                else:
                    data[col] = jdatetime.date.today()
                continue

            if isinstance(val, str):
                stripped = val.strip()
                if stripped:
                    try:
                        if is_datetime:
                            data[col] = dt.datetime.fromisoformat(stripped)
                        else:
                            data[col] = _parse_shamsi_date(stripped)
                    except Exception:
                        data[col] = dt.datetime.now() if is_datetime else jdatetime.date.today()
                else:
                    data[col] = dt.datetime.now() if is_datetime else jdatetime.date.today()
                continue

            if isinstance(val, (int, float)):
                try:
                    base = dt.datetime(1899, 12, 30)
                    delta = dt.timedelta(days=int(val))
                    if isinstance(val, float) and val % 1 != 0:
                        delta += dt.timedelta(seconds=round((val % 1) * 86400))
                    greg = base + delta
                    if is_datetime:
                        data[col] = greg
                    else:
                        data[col] = jdatetime.date.fromgregorian(date=greg.date())
                except Exception:
                    data[col] = dt.datetime.now() if is_datetime else jdatetime.date.today()
                continue

            if isinstance(val, dt.date):
                try:
                    if isinstance(val, dt.datetime):
                        data[col] = val if is_datetime else jdatetime.date.fromgregorian(date=val.date())
                    else:
                        if is_datetime:
                            data[col] = dt.datetime.combine(val, dt.time.min)
                        else:
                            data[col] = jdatetime.date.fromgregorian(date=val)
                except Exception:
                    data[col] = dt.datetime.now() if is_datetime else jdatetime.date.today()
                continue

            data[col] = dt.datetime.now() if is_datetime else jdatetime.date.today()
    return data


def convert_dates_for_export(model, df):
    for field in model._meta.get_fields():
        if isinstance(field, (models.DateField, models.DateTimeField)):
            col = field.name
            if col in df.columns:
                is_datetime = isinstance(field, models.DateTimeField)
                df[col] = df[col].apply(
                    lambda d: _gregorian_to_shamsi_str(d, is_datetime=is_datetime) if pd.notnull(d) else ''
                )
    return df


def _parse_shamsi_date(date_str):
    parts = re.split(r'[-/]', date_str.strip())
    if len(parts) == 3:
        try:
            y, m, d = map(int, parts)
            return jdatetime.date(y, m, d)
        except (ValueError, TypeError):
            pass
    return jdatetime.date.today()


def clean_data_for_model(model, data):
    NA_STRINGS = {'nan', 'none', 'null', 'na', ''}
    for field in model._meta.get_fields():
        if not field.is_relation and hasattr(field, 'null'):
            field_name = field.name
            if field_name not in data:
                continue
            value = data[field_name]

            if isinstance(value, float) and not math.isnan(value) and value == int(value):
                value = int(value)

            if isinstance(value, str) and value.strip().lower() in NA_STRINGS:
                value = None
            elif isinstance(value, float) and math.isnan(value):
                value = None

            if isinstance(field, (models.DateField, models.DateTimeField)):
                continue

            if value is None:
                if isinstance(field, (models.CharField, models.TextField)):
                    data[field_name] = ''
                elif isinstance(field, (models.IntegerField, models.DecimalField, models.FloatField)):
                    if field.has_default():
                        del data[field_name]
                    else:
                        data[field_name] = 0
                elif isinstance(field, models.JSONField):
                    data[field_name] = {}
                elif isinstance(field, models.BooleanField):
                    data[field_name] = False
                else:
                    if not field.null:
                        del data[field_name]
            else:
                if isinstance(field, models.CharField) and not isinstance(value, str):
                    data[field_name] = str(value)


def resolve_foreign_keys(model, data):
    for field in model._meta.get_fields():
        if field.is_relation and field.many_to_one:
            fk_attname = field.attname
            if fk_attname in data:
                fk_value = data[fk_attname]
                if fk_value is not None and not (isinstance(fk_value, float) and math.isnan(fk_value)):
                    related_model = field.related_model
                    try:
                        obj = related_model.objects.get(pk=int(fk_value))
                        data[field.name] = obj
                    except (related_model.DoesNotExist, ValueError, TypeError):
                        pass
                del data[fk_attname]


@login_required
@admin_or_manager_required
def export_all_data(request):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for model_name in MODEL_ORDER:
            model = get_model_by_name(model_name)
            if not model:
                continue
            queryset = model.objects.all()
            df = pd.DataFrame(list(queryset.values()))
            for col in ['qr_code', 'image', 'password']:
                if col in df.columns:
                    df.drop(col, axis=1, inplace=True)
            df = convert_dates_for_export(model, df)
            df.to_excel(writer, sheet_name=model_name, index=False)

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="selvi_all_data.xlsx"'
    return response


@login_required
@admin_or_manager_required
def import_data(request):
    if request.method == 'POST':
        file = request.FILES.get('excel_file')
        if not file:
            messages.error(request, 'فایلی انتخاب نشده است.')
            return redirect('import_data')

        try:
            xls = pd.ExcelFile(file)
            sheets_processed = 0
            for sheet_name in MODEL_ORDER:
                if sheet_name not in xls.sheet_names:
                    continue
                model = get_model_by_name(sheet_name)
                if not model:
                    continue

                df = pd.read_excel(file, sheet_name=sheet_name)
                df = df.where(pd.notnull(df), None)

                for _, row in df.iterrows():
                    data = row.to_dict()
                    data.pop('qr_code', None)
                    data.pop('image', None)

                    raw_id = data.pop('id', None)

                    data = convert_dates_for_import(model, data)
                    clean_data_for_model(model, data)
                    resolve_foreign_keys(model, data)

                    valid_id = None
                    if raw_id is not None:
                        if isinstance(raw_id, (int, float)):
                            if not math.isnan(raw_id):
                                valid_id = int(raw_id)
                        elif isinstance(raw_id, str):
                            raw_id = raw_id.strip()
                            if raw_id.lower() not in {'nan', 'none', 'null', ''}:
                                try:
                                    valid_id = int(float(raw_id))
                                except ValueError:
                                    pass

                    if valid_id is not None:
                        model.objects.update_or_create(id=valid_id, defaults=data)
                    else:
                        model.objects.create(**data)

                sheets_processed += 1

            messages.success(request, f'{sheets_processed} جدول با موفقیت پردازش شدند.')
        except Exception as e:
            import traceback as _tb
            logger.error("Import failed with traceback:")
            logger.error(_tb.format_exc())
            messages.error(request, f'خطا در پردازش فایل: {e}')

        return redirect('import_data')

    return render(request, 'production/import_data.html')


# === CHUNK 5 END ===


@login_required
def scan_packaging_unit(request, pk):
    unit = get_object_or_404(PackagingUnit, pk=pk)
    worker_stage = request.user.worker_profile.stage if hasattr(request.user, 'worker_profile') else None
    next_url = request.GET.get('next', 'dashboard')

    if request.method == 'POST':
        if worker_stage == 'packaging':
            if not unit.is_packed:
                unit.is_packed = True
                unit.packed_at = timezone.now()
                unit.packed_by = request.user
                unit.save()

                item = unit.order_item
                if item.is_fully_packed and not ProductionLog.objects.filter(
                    order_item=item, stage='packaging'
                ).exists():
                    ProductionLog.objects.create(
                        order_item=item, stage='packaging', user=request.user,
                        notes='همه واحدها بسته‌بندی شدند'
                    )
                messages.success(request, f'✅ واحد {unit.unit_number} بسته‌بندی شد.')
            else:
                messages.warning(request, 'این واحد قبلاً بسته‌بندی شده است.')

        elif worker_stage == 'shipping':
            if not unit.is_packed:
                messages.error(request, '⛔ این واحد هنوز بسته‌بندی نشده است. ابتدا باید بسته‌بندی شود.')
                return redirect(next_url)

            plate = request.POST.get('plate', '').strip()
            if not plate:
                messages.error(request, 'لطفاً پلاک خودرو را وارد کنید.')
                context = {
                    'unit': unit,
                    'can_pack': False,
                    'can_ship': True,
                    'next_url': next_url,
                    'saved_plate': request.session.get('current_plate', ''),
                }
                return render(request, 'production/scan_packaging_unit.html', context)

            request.session['current_plate'] = plate

            if not unit.is_shipped:
                unit.is_shipped = True
                unit.shipped_at = timezone.now()
                unit.shipped_by = request.user
                unit.save()

                ShipmentLog.objects.create(
                    packaging_unit=unit,
                    plate_number=plate,
                    shipped_by=request.user
                )

                item = unit.order_item
                if item.is_fully_shipped and not ProductionLog.objects.filter(
                    order_item=item, stage='shipping'
                ).exists():
                    ProductionLog.objects.create(
                        order_item=item, stage='shipping', user=request.user,
                        notes='همه واحدها ارسال شدند'
                    )
                messages.success(request, f'🚚 واحد {unit.unit_number} ارسال شد.')
            else:
                messages.warning(request, 'این واحد قبلاً ارسال شده است.')

        else:
            messages.error(request, 'شما دسترسی لازم برای این عملیات را ندارید.')

        return redirect(next_url)

    context = {
        'unit': unit,
        'can_pack': worker_stage == 'packaging' and not unit.is_packed,
        'can_ship': worker_stage == 'shipping' and unit.is_packed and not unit.is_shipped,
        'next_url': next_url,
        'saved_plate': request.session.get('current_plate', ''),
    }
    return render(request, 'production/scan_packaging_unit.html', context)


@login_required
def undo_packaging_unit(request, pk):
    unit = get_object_or_404(PackagingUnit, pk=pk)
    worker_stage = request.user.worker_profile.stage if hasattr(request.user, 'worker_profile') else None

    if worker_stage not in ['packaging', 'shipping']:
        messages.error(request, 'شما دسترسی لازم برای لغو عملیات را ندارید.')
        return redirect('dashboard')

    if worker_stage == 'packaging':
        if not unit.is_packed:
            messages.warning(request, 'این واحد هنوز بسته‌بندی نشده است.')
        elif unit.packed_by != request.user and not request.user.is_superuser:
            messages.error(request, 'فقط اپراتوری که این واحد را بسته‌بندی کرده می‌تواند آن را لغو کند.')
        else:
            unit.is_packed = False
            unit.packed_at = None
            unit.packed_by = None
            unit.save()

            ProductionLog.objects.filter(order_item=unit.order_item, stage='packaging').delete()
            messages.success(request, f'✅ بسته‌بندی واحد {unit.unit_number} لغو شد.')

    elif worker_stage == 'shipping':
        if not unit.is_shipped:
            messages.warning(request, 'این واحد هنوز ارسال نشده است.')
        elif unit.shipped_by != request.user and not request.user.is_superuser:
            messages.error(request, 'فقط اپراتوری که این واحد را ارسال کرده می‌تواند آن را لغو کند.')
        else:
            unit.is_shipped = False
            unit.shipped_at = None
            unit.shipped_by = None
            unit.save()

            ShipmentLog.objects.filter(packaging_unit=unit).delete()
            ProductionLog.objects.filter(order_item=unit.order_item, stage='shipping').delete()
            messages.success(request, f'🚚 ارسال واحد {unit.unit_number} لغو شد.')

    next_url = request.GET.get('next', 'dashboard')
    return redirect(next_url)


@login_required
def customer_order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'production/customer/order_list.html', {'orders': orders})


@login_required
def customer_create_order_step1(request):
    existing_customer = Customer.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = CustomerInfoForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data.get('phone', '')
            address = form.cleaned_data.get('address', '')
            number = form.cleaned_data.get('number', '')

            customer = Customer.objects.create(
                user=request.user,
                name=name,
                phone=phone,
                address=address
            )

            order = Order.objects.create(
                user=request.user,
                customer=customer,
                number=number,
                status='draft'
            )
            messages.success(request, 'سفارش جدید ایجاد شد. حالا محصولات را اضافه کنید.')
            return redirect('customer_create_order_step2', order_id=order.id)
    else:
        initial = {}
        if existing_customer:
            initial = {
                'name': existing_customer.name,
                'phone': existing_customer.phone,
                'address': existing_customer.address,
            }
        form = CustomerInfoForm(initial=initial)

    return render(request, 'production/customer/step1.html', {'form': form})


@login_required
def customer_create_order_step2(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    existing_items = order.items.select_related('product__category').prefetch_related('ordercolor')

    if request.method == 'POST':
        item_form = OrderItemForm(request.POST)
        color_form = ColorSelectionForm(request.POST)
        if item_form.is_valid() and color_form.is_valid():
            with transaction.atomic():
                product = item_form.cleaned_data['product']
                order_item = item_form.save(commit=False)
                order_item.order = order
                order_item.product = product
                order_item.unit_price = product.base_price
                order_item.save()

                for part_value, _ in OrderColor.PART_CHOICES:
                    code = color_form.cleaned_data.get(f'color_{part_value}')
                    if code:
                        OrderColor.objects.create(part=part_value, code=code, orderitem=order_item)
                messages.success(request, f'{order_item.product.name} به سفارش اضافه شد.')
                if 'add_another' in request.POST:
                    return redirect('customer_create_order_step2', order_id=order.id)
                else:
                    return redirect('order_invoice', order_id=order.id)
        else:
            messages.error(request, 'لطفاً خطاهای فرم را بررسی کنید.')
    else:
        item_form = OrderItemForm()
        color_form = ColorSelectionForm()

    context = {
        'order': order,
        'item_form': item_form,
        'color_form': color_form,
        'existing_items': existing_items,
    }
    return render(request, 'production/customer/step2.html', context)


@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items__product__category', 'items__ordercolor'), id=order_id)
    if not (request.user.is_superuser or order.user == request.user):
        return HttpResponseForbidden()
    return render(request, 'production/order_invoice.html', {'order': order})


# === CHUNK 6 END ===


@login_required
def customer_edit_order_item(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)

    if item.order.user != request.user:
        messages.error(request, "شما اجازه ویرایش این آیتم را ندارید.")
        return redirect('customer_order_list')

    if not (item.order.status == 'draft' and item.order.created_at == jdatetime.date.today()):
        messages.error(request, "فقط سفارش‌های پیش‌نویس امروز قابل ویرایش هستند.")
        return redirect('customer_order_detail', order_id=item.order.id)

    existing_colors = {c.part: c.code for c in item.ordercolor.all()}

    if request.method == 'POST':
        item_form = EditOrderItemForm(request.POST, instance=item)
        color_form = ColorSelectionForm(request.POST)

        if item_form.is_valid() and color_form.is_valid():
            with transaction.atomic():
                new_product = item_form.cleaned_data['product']
                if item.product != new_product:
                    item.product = new_product
                    item.unit_price = new_product.base_price
                item_form.save()

                item.ordercolor.all().delete()
                for part_value, _ in OrderColor.PART_CHOICES:
                    code = color_form.cleaned_data.get(f'color_{part_value}')
                    if code:
                        OrderColor.objects.create(part=part_value, code=code, orderitem=item)

                messages.success(request, "آیتم با موفقیت ویرایش شد.")
                return redirect('customer_order_detail', order_id=item.order.id)
    else:
        item_form = EditOrderItemForm(instance=item)
        color_form = ColorSelectionForm(initial={
            f'color_{part}': existing_colors.get(part, '')
            for part, _ in OrderColor.PART_CHOICES
        })

    return render(request, 'production/customer/edit_order_item.html', {
        'item_form': item_form,
        'color_form': color_form,
        'item': item,
    })


@login_required
def customer_order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.user != request.user:
        messages.error(request, "شما اجازه مشاهده این سفارش را ندارید.")
        return redirect('customer_order_list')

    can_edit = (order.status == 'draft' and order.created_at == jdatetime.date.today())

    add_item_form = OrderItemForm()
    add_color_form = ColorSelectionForm()

    context = {
        'order': order,
        'can_edit': can_edit,
        'add_item_form': add_item_form,
        'add_color_form': add_color_form,
        'edit_customer_form': CustomerInfoForm(initial={
            'name': order.customer.name,
            'phone': order.customer.phone,
            'address': order.customer.address,
            'number': order.number,
        }),
    }
    return render(request, 'production/customer/order_detail.html', context)


@login_required
def customer_edit_order_info(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if not (order.status == 'draft' and order.created_at == jdatetime.date.today()):
        messages.error(request, "فقط سفارش‌های پیش‌نویس امروز قابل ویرایش هستند.")
        return redirect('customer_order_detail', order_id=order.id)

    if request.method == 'POST':
        form = CustomerInfoForm(request.POST)
        if form.is_valid():
            customer = order.customer
            customer.name = form.cleaned_data['name']
            customer.phone = form.cleaned_data.get('phone', '')
            customer.address = form.cleaned_data.get('address', '')
            customer.save()

            order.number = form.cleaned_data.get('number', '')
            order.save()

            messages.success(request, "اطلاعات سفارش به‌روز شد.")
            return redirect('customer_order_detail', order_id=order.id)

    return redirect('customer_order_detail', order_id=order.id)


@login_required
def customer_add_item(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if not (order.status == 'draft' and order.created_at == jdatetime.date.today()):
        messages.error(request, "فقط سفارش‌های پیش‌نویس امروز قابل ویرایش هستند.")
        return redirect('customer_order_detail', order_id=order.id)

    if request.method == 'POST':
        item_form = OrderItemForm(request.POST)
        color_form = ColorSelectionForm(request.POST)
        if item_form.is_valid() and color_form.is_valid():
            with transaction.atomic():
                product = item_form.cleaned_data['product']
                order_item = item_form.save(commit=False)
                order_item.order = order
                order_item.product = product
                order_item.unit_price = product.base_price
                order_item.save()

                for part_value, _ in OrderColor.PART_CHOICES:
                    code = color_form.cleaned_data.get(f'color_{part_value}')
                    if code:
                        OrderColor.objects.create(part=part_value, code=code, orderitem=order_item)

                messages.success(request, f'{product.name} به سفارش اضافه شد.')
                return redirect('customer_order_detail', order_id=order.id)
        else:
            messages.error(request, 'لطفاً خطاهای فرم را بررسی کنید.')
    return redirect('customer_order_detail', order_id=order.id)


@login_required
def customer_delete_order_item(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)
    if item.order.user != request.user:
        messages.error(request, "شما اجازه حذف این آیتم را ندارید.")
        return redirect('customer_order_list')
    if not (item.order.status == 'draft' and item.order.created_at == jdatetime.date.today()):
        messages.error(request, "فقط سفارش‌های پیش‌نویس امروز قابل تغییر هستند.")
        return redirect('customer_order_list')

    order_id = item.order.id
    item_name = item.product.name
    item.delete()
    messages.success(request, f"آیتم «{item_name}» با موفقیت حذف شد.")
    return redirect('customer_order_detail', order_id=order_id)


@login_required
def order_combined_print(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items__product__category',
            'items__product__bom__part',
            'items__ordercolor',
            'items__packaging_units',
        ),
        id=order_id
    )

    items_data = []
    for item in order.items.all():
        item.color = item.color_summary

        bom_list = item.product.bom.all()
        item.bompart = [{'part': b.part, 'quantity': b.quantity} for b in bom_list]

        units = item.packaging_units.all()

        items_data.append({
            'item': item,
            'units': units,
        })

    context = {
        'order': order,
        'items_data': items_data,
    }
    return render(request, 'production/order_combined_print.html', context)


# === CHUNK 7 END ===


@login_required
@staff_or_representative_required
def report_shipped(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            y, m, d = map(int, date_str.split('-'))
            persian_date = jdatetime.date(y, m, d)
        except (ValueError, TypeError):
            persian_date = jdatetime.date.today()
    else:
        persian_date = jdatetime.date.today()

    gregorian_date = persian_date.togregorian()

    units = PackagingUnit.objects.filter(
        is_shipped=True,
        shipped_at__date=gregorian_date
    ).select_related(
        'order_item__order__customer',
        'order_item__order__user',
        'order_item__product__category',
        'shipped_by'
    ).prefetch_related(
        'order_item__ordercolor',
        'shipment_logs'
    )
    units = units.order_by('order_item__product__category__name', 'order_item__product__name')

    plate = request.GET.get('plate')
    if plate:
        units = units.filter(shipment_logs__plate_number=plate)

    representative_id = request.GET.get('representative')
    if representative_id:
        units = units.filter(order_item__order__user_id=representative_id)

    order_id = request.GET.get('order_id')
    if order_id:
        units = units.filter(order_item__order_id=order_id)

    representative_name = ""
    total_price = 0
    if units.exists():
        if representative_id:
            try:
                rep = User.objects.get(pk=representative_id)
                representative_name = rep.get_full_name() or rep.username
            except User.DoesNotExist:
                pass
        else:
            representative_name = units.first().order_item.order.user.get_full_name() or units.first().order_item.order.user.username
        total_price = sum(unit.order_item.unit_price for unit in units)

    if request.GET.get('print'):
        return render(request, 'production/reports/delivery_note.html', {
            'units': units,
            'today': persian_date,
            'representative_name': representative_name,
            'total_price': total_price,
            'plate': request.GET.get('plate', ''),
        })

    representatives = User.objects.filter(
        order__items__packaging_units__is_shipped=True
    ).distinct().order_by('username')

    plates = ShipmentLog.objects.values_list('plate_number', flat=True).distinct().order_by('plate_number')

    context = {
        'units': units,
        'representatives': representatives,
        'selected_representative': representative_id,
        'selected_date': persian_date.strftime('%Y-%m-%d'),
        'selected_order': order_id or '',
        'representative_name': representative_name,
        'total_price': total_price,
        'plates': plates,
        'selected_plate': plate or '',
    }
    return render(request, 'production/reports/shipped.html', context)


@login_required
@admin_or_manager_required
def product_create(request):
    BOMFormSet = inlineformset_factory(
        Product, ProductBOM,
        fields=['part', 'quantity', 'size_adjustment_rule', 'color_part', 'color_material_map'],
        extra=1, can_delete=True,
        widgets={
            'part': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'size_adjustment_rule': forms.HiddenInput(attrs={'class': 'size-rule-hidden'}),
            'color_part': forms.Select(attrs={'class': 'form-select color-part-select'}),
            'color_material_map': forms.HiddenInput(),
        }
    )

    if request.method == 'POST':
        product_form = ProductCreateForm(request.POST)
        formset = BOMFormSet(request.POST, prefix='bom')

        if product_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = product_form.save(commit=False)
                default_colors = {}
                for part, _ in OrderColor.PART_CHOICES:
                    field_name = f'color_{part}'
                    code = product_form.cleaned_data.get(field_name)
                    if code:
                        default_colors[part] = code
                product.default_colors = default_colors
                product.save()

                instances = formset.save(commit=False)
                for bom in instances:
                    bom.product = product
                    bom.size_affected = bool(bom.size_adjustment_rule)
                    bom.save()
                for obj in formset.deleted_objects:
                    obj.delete()

                messages.success(request, '✅ محصول و قطعات با موفقیت ذخیره شدند.')
                return redirect('admin_product_list')
    else:
        product_form = ProductCreateForm()
        formset = BOMFormSet(prefix='bom')

    context = {
        'product_form': product_form,
        'formset': formset,
        'product': None,
        'materials': Material.objects.all(),
        'all_parts': Part.objects.all(),
    }
    return render(request, 'production/product_create.html', context)


@login_required
@admin_or_manager_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    BOMFormSet = inlineformset_factory(
        Product, ProductBOM,
        fields=['part', 'quantity', 'size_adjustment_rule', 'color_part', 'color_material_map'],
        extra=0, can_delete=True,
        widgets={
            'part': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'size_adjustment_rule': forms.HiddenInput(attrs={'class': 'size-rule-hidden'}),
            'color_part': forms.Select(attrs={'class': 'form-select color-part-select'}),
            'color_material_map': forms.HiddenInput(),
        }
    )

    if request.method == 'POST':
        product_form = ProductCreateForm(request.POST, instance=product)
        formset = BOMFormSet(request.POST, prefix='bom', instance=product)

        if product_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = product_form.save(commit=False)
                default_colors = {}
                for part, _ in OrderColor.PART_CHOICES:
                    field_name = f'color_{part}'
                    code = product_form.cleaned_data.get(field_name)
                    if code:
                        default_colors[part] = code
                product.default_colors = default_colors
                product.save()

                instances = formset.save(commit=False)
                for bom in instances:
                    bom.product = product
                    bom.size_affected = bool(bom.size_adjustment_rule)
                    bom.save()
                for obj in formset.deleted_objects:
                    obj.delete()

                messages.success(request, '✅ محصول با موفقیت ویرایش شد.')
                return redirect('admin_product_list')
    else:
        product_form = ProductCreateForm(instance=product)
        formset = BOMFormSet(prefix='bom', instance=product)

    context = {
        'product_form': product_form,
        'formset': formset,
        'product': product,
        'materials': Material.objects.all(),
        'all_parts': Part.objects.all(),
    }
    return render(request, 'production/product_create.html', context)


@login_required
@admin_or_manager_required
def ajax_create_part(request):
    if request.method == 'POST':
        form = PartForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.f2 = part.name
            part.save()
            return JsonResponse({'success': True, 'id': part.id, 'name': str(part)})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False})


@login_required
@admin_or_manager_required
def ajax_get_part(request, part_id):
    part = get_object_or_404(Part, pk=part_id)
    data = {
        'id': part.id,
        'name': part.name,
        'material': part.material_id,
        'length': str(part.length),
        'width': str(part.width),
        'grain': part.grain,
        'pname': part.pname,
        'turn': part.turn,
        'f26': part.f26,
        'f18': part.f18,
        'f4': part.f4,
        'f5': part.f5,
        'f3': part.f3,
        'routing_code': part.routing_code,
        'base_part': part.base_part_id,
    }
    return JsonResponse(data)


@login_required
@admin_or_manager_required
def ajax_edit_part(request, part_id):
    part = get_object_or_404(Part, pk=part_id)
    if request.method == 'POST':
        form = PartForm(request.POST, instance=part)
        if form.is_valid():
            part = form.save(commit=False)
            part.f2 = part.name
            part.save()
            return JsonResponse({'success': True, 'id': part.id, 'name': str(part)})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False})


@login_required
@admin_or_manager_required
def set_plate(request):
    if request.method == 'POST':
        plate = request.POST.get('plate', '').strip()
        if plate:
            request.session['current_plate'] = plate
            messages.success(request, f'پلاک "{plate}" برای بارگیری فعال شد.')
        else:
            request.session.pop('current_plate', None)
            messages.warning(request, 'پلاک پاک شد.')
        return redirect('scan_part')
    current_plate = request.session.get('current_plate', '')
    return render(request, 'production/set_plate.html', {'current_plate': current_plate})


@login_required
def select_shipment(request):
    if request.method == 'GET':
        plate = request.GET.get('plate', '').strip()
        if plate:
            request.session['current_plate'] = plate
        return redirect('scan_part')
    return redirect('scan_part')


# === CHUNK 8 END ===


@login_required
def customer_shipments(request):
    orders = Order.objects.filter(user=request.user)

    shipments = (
        PackagingUnit.objects
        .filter(order_item__order__in=orders, is_shipped=True)
        .select_related(
            'order_item__order__customer',
            'order_item__product__category',
            'order_item__order__user'
        )
        .prefetch_related('shipment_logs', 'order_item__ordercolor')
        .order_by('-shipped_at')
    )

    groups = {}
    for unit in shipments:
        log = unit.shipment_logs.first()
        if log:
            key = f"{log.plate_number}_{log.shipped_at.date()}"
            if key not in groups:
                groups[key] = {
                    'plate': log.plate_number,
                    'date': log.shipped_at,
                    'units': [],
                    'total_price': 0,
                }
            groups[key]['units'].append(unit)
            groups[key]['total_price'] += int(unit.order_item.unit_price or 0)

    shipment_groups = list(groups.values())
    shipment_groups.sort(key=lambda x: x['date'], reverse=True)

    context = {
        'shipment_groups': shipment_groups,
    }
    return render(request, 'production/customer/shipments.html', context)


@login_required
def customer_shipment_detail(request, plate, date):
    try:
        ship_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'تاریخ نامعتبر است.')
        return redirect('customer_shipments')

    orders = Order.objects.filter(user=request.user)

    units = (
        PackagingUnit.objects
        .filter(
            order_item__order__in=orders,
            is_shipped=True,
            shipment_logs__plate_number=plate,
            shipped_at__date=ship_date
        )
        .select_related(
            'order_item__order__customer',
            'order_item__product__category',
            'order_item__order__user'
        )
        .prefetch_related('shipment_logs', 'order_item__ordercolor')
        .order_by('order_item__order__id', 'order_item__product__name')
    )

    if not units.exists():
        messages.warning(request, 'هیچ ارسالی با این مشخصات یافت نشد.')
        return redirect('customer_shipments')

    first_unit = units.first()
    representative = first_unit.order_item.order.user
    representative_name = representative.get_full_name() or representative.username
    customer_name = first_unit.order_item.order.customer.name

    total_price = sum(int(u.order_item.unit_price or 0) for u in units)

    shamsi_date = jdatetime.date.fromgregorian(date=ship_date).strftime('%Y/%m/%d')

    context = {
        'units': units,
        'plate': plate,
        'date': ship_date,
        'shamsi_date': shamsi_date,
        'representative_name': representative_name,
        'customer_name': customer_name,
        'total_price': total_price,
    }
    return render(request, 'production/customer/shipment_detail.html', context)


@login_required
@admin_or_manager_required
def assign_painting_process(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)

    if request.method == 'POST':
        with transaction.atomic():
            existing_paint_tasks = ProductionTask.objects.filter(
                order=item.order,
                station_name='paint',
                order_item=item
            )
            if existing_paint_tasks.filter(status='done').exists():
                messages.error(
                    request,
                    "❌ برخی از مراحل نقاشی این آیتم قبلاً انجام شده‌اند. "
                    "برای جلوگیری از از دست رفتن سابقه، ابتدا آن‌ها را به صورت دستی مدیریت کنید."
                )
                return redirect('item_detail', pk=item_id)

            existing_paint_tasks.delete()

            global_base = ProductionTask.objects.filter(order=item.order).aggregate(
                max_step=models.Max('step_order')
            )['max_step'] or 0

            new_tasks = []
            errors = []

            assignments = get_item_color_assignments(item)

            if not assignments:
                errors.append("⚠️ هیچ کد رنگی برای این آیتم یافت نشد.")

            for part_name, color_code in assignments:
                painting_process = get_painting_process_for_color(color_code)
                if not painting_process:
                    errors.append(f"❌ {part_name} (کد رنگ {color_code}): روند نقاشی فعالی یافت نشد.")
                    continue

                create_paint_tasks(
                    tasks_list=new_tasks,
                    order=item.order,
                    quantity=item.quantity,
                    process=painting_process,
                    base_step=global_base,
                    order_item=item,
                    color_part=part_name
                )
                global_base += painting_process.stages.count()

            if new_tasks:
                ProductionTask.objects.bulk_create(new_tasks)
                messages.success(
                    request,
                    f"✅ {len(new_tasks)} تسک نقاشی برای آیتم {item.id} ایجاد شد."
                )
                for err in errors:
                    messages.warning(request, err)
            else:
                for err in errors:
                    messages.error(request, err)
                messages.error(request, "❌ هیچ تسک نقاشی‌ای ایجاد نشد.")

        return redirect('item_detail', pk=item_id)

    color_codes = get_unique_color_codes_for_item(item)
    ROKESHI_CODES = {'8', '9', '10', '11'}
    color_info = [{'code': c, 'is_rokeshi': c in ROKESHI_CODES} for c in color_codes]
    return render(request, 'production/assign_painting.html', {
        'item': item,
        'color_info': color_info,
        'has_colors': item.ordercolor.exists() or bool(item.product.default_colors),
    })


@login_required
@admin_or_manager_required
def daily_schedule_print(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            y, m, d = map(int, date_str.split('-'))
            selected_date = jdatetime.date(y, m, d)
        except (ValueError, TypeError):
            selected_date = jdatetime.date.today()
    else:
        selected_date = jdatetime.date.today()

    gregorian_date = selected_date.togregorian()

    tasks = list(
        ProductionTask.objects.filter(
            station_name='paint',
            scheduled_start__date=gregorian_date
        ).select_related(
            'order_item__product__category',
            'order_item__order__user',
            'painting_stage',
            'assigned_worker',
            'order_item__order__customer'
        ).order_by('assigned_worker_id', 'scheduled_start')
    )

    tasks_by_worker = {}
    for task in tasks:
        key = task.assigned_worker_id
        tasks_by_worker.setdefault(key, []).append(task)

    worker_ids = [k for k in tasks_by_worker if k is not None]
    workers = WorkerProfile.objects.filter(user_id__in=worker_ids).select_related('user')
    workers_map = {wp.user_id: wp for wp in workers}

    worker_columns = []
    for worker_id, worker_tasks in tasks_by_worker.items():
        if worker_id is None:
            continue
        worker_profile = workers_map.get(worker_id)
        if worker_profile:
            user = worker_profile.user
            label = user.get_full_name() or user.username
            skills = worker_profile.skills or []
        else:
            label = f"کارگر #{worker_id}"
            skills = []

        total_duration = sum(
            t.painting_stage.duration_minutes if t.painting_stage else 0
            for t in worker_tasks
        )

        worker_columns.append({
            'worker_id': worker_id,
            'label': label,
            'skills': skills,
            'tasks': worker_tasks,
            'total_duration': total_duration,
        })

    worker_columns.sort(key=lambda x: x['label'])

    context = {
        'worker_columns': worker_columns,
        'selected_date': selected_date,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'gregorian_date': gregorian_date,
        'today_str': jdatetime.date.today().strftime('%Y/%m/%d'),
        'yesterday': (selected_date - jdatetime.timedelta(days=1)).strftime('%Y-%m-%d'),
        'tomorrow': (selected_date + jdatetime.timedelta(days=1)).strftime('%Y-%m-%d'),
    }
    return render(request, 'production/daily_schedule_print.html', context)


@login_required
@admin_or_manager_required
def auto_assign_tasks_view(request):
    if request.method == 'POST':
        auto_assign_paint_tasks()
        messages.success(request, "تخصیص خودکار کارگران انجام شد.")
    return redirect('dashboard')


# === CHUNK 9 END ===


@login_required
@admin_or_manager_required
def painting_management_dashboard(request):
    recent_tasks = ProductionTask.objects.filter(
        station_name='paint'
    ).select_related('order', 'part', 'painting_stage', 'assigned_worker', 'order_item__product').order_by('-id')[:10]

    context = {
        'active_tab': 'dashboard',
        'total_processes': PaintingProcess.objects.count(),
        'active_processes': PaintingProcess.objects.filter(is_active=True).count(),
        'total_stages': PaintingStage.objects.count(),
        'total_workers': WorkerProfile.objects.filter(stage='paint').count(),
        'pending_tasks': ProductionTask.objects.filter(station_name='paint', status__in=['pending', 'waiting']).count(),
        'unassigned_tasks': ProductionTask.objects.filter(station_name='paint', assigned_worker__isnull=True, status__in=['pending', 'waiting']).count(),
        'ready_items_count': get_painting_ready_items_queryset().count(),
        'unscheduled_ready_count': get_unscheduled_ready_items().count(),
        'recent_tasks': recent_tasks,
        **painting_nav_context(),
    }
    return render(request, 'production/painting_management/dashboard.html', context)


@login_required
@admin_or_manager_required
def painting_processes_view(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')

        if action == 'create':
            form = PaintingProcessForm(request.POST)
            if form.is_valid():
                process = form.save()
                return JsonResponse({'success': True, 'id': process.id, 'name': process.name})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif action == 'edit':
            process_id = request.POST.get('process_id')
            process = get_object_or_404(PaintingProcess, pk=process_id)
            form = PaintingProcessForm(request.POST, instance=process)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif action == 'delete':
            process_id = request.POST.get('process_id')
            process = get_object_or_404(PaintingProcess, pk=process_id)
            process.delete()
            return JsonResponse({'success': True})

        elif action == 'toggle_active':
            process_id = request.POST.get('process_id')
            process = get_object_or_404(PaintingProcess, pk=process_id)
            process.is_active = not process.is_active
            process.save()
            return JsonResponse({'success': True, 'is_active': process.is_active})

    processes = PaintingProcess.objects.all().annotate(stage_count=Count('stages')).order_by('-is_active', 'name')

    search = request.GET.get('search')
    if search:
        processes = processes.filter(Q(name__icontains=search) | Q(code__icontains=search))

    paginator = Paginator(processes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'active_tab': 'processes',
        'processes': page_obj,
        'search': search,
        'form': PaintingProcessForm(),
        **painting_nav_context(),
    }
    return render(request, 'production/painting_management/processes.html', context)


@login_required
@admin_or_manager_required
def painting_process_detail_api(request, process_id):
    process = get_object_or_404(PaintingProcess, pk=process_id)
    return JsonResponse({
        'id': process.id,
        'name': process.name,
        'code': process.code,
        'color_codes': process.color_codes or [],
        'is_active': process.is_active,
        'description': process.description or '',
    })


@login_required
@admin_or_manager_required
def painting_stages_view(request, process_id=None):
    process = None
    if process_id:
        process = get_object_or_404(PaintingProcess, pk=process_id)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')

        if action == 'create':
            form = PaintingStageForm(request.POST)
            if form.is_valid():
                stage = form.save()
                return JsonResponse({'success': True, 'id': stage.id, 'name': stage.name})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif action == 'edit':
            stage_id = request.POST.get('stage_id')
            stage = get_object_or_404(PaintingStage, pk=stage_id)
            form = PaintingStageForm(request.POST, instance=stage)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif action == 'delete':
            stage_id = request.POST.get('stage_id')
            stage = get_object_or_404(PaintingStage, pk=stage_id)
            stage.delete()
            return JsonResponse({'success': True})

        elif action == 'reorder':
            stage_ids = request.POST.getlist('stage_ids[]')
            with transaction.atomic():
                stages = list(PaintingStage.objects.filter(pk__in=stage_ids))
                stage_map = {str(s.pk): s for s in stages}

                for offset, stage_id in enumerate(stage_ids, start=1):
                    stage = stage_map[str(stage_id)]
                    stage.order = -offset
                    stage.save(update_fields=['order'])

                for idx, stage_id in enumerate(stage_ids, start=1):
                    stage = stage_map[str(stage_id)]
                    stage.order = idx
                    stage.save(update_fields=['order'])

            return JsonResponse({'success': True})

    stages = PaintingStage.objects.all()
    if process:
        stages = stages.filter(process=process)
    stages = stages.select_related('process').order_by('process__name', 'order')

    search = request.GET.get('search')
    if search:
        stages = stages.filter(Q(name__icontains=search) | Q(process__name__icontains=search))

    paginator = Paginator(stages, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'active_tab': 'stages',
        'stages': page_obj,
        'process': process,
        'search': search,
        'form': PaintingStageForm(),
        'processes': PaintingProcess.objects.all(),
        **painting_nav_context(),
    }
    return render(request, 'production/painting_management/stages.html', context)


@login_required
@admin_or_manager_required
def painting_stage_detail_api(request, stage_id):
    stage = get_object_or_404(PaintingStage, pk=stage_id)
    return JsonResponse({
        'id': stage.id,
        'process': stage.process_id,
        'order': stage.order,
        'name': stage.name,
        'duration_minutes': stage.duration_minutes,
        'drying_time_minutes': stage.drying_time_minutes,
        'required_skill': stage.required_skill,
    })


@login_required
@admin_or_manager_required
def painting_workers_view(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')

        if action == 'create':
            form = WorkerProfileForm(request.POST)
            if form.is_valid():
                worker = form.save()
                return JsonResponse({'success': True, 'id': worker.id, 'name': worker.user.username})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif action == 'edit':
            worker_id = request.POST.get('worker_id')
            worker = get_object_or_404(WorkerProfile, pk=worker_id)
            form = WorkerProfileForm(request.POST, instance=worker)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': form.errors})

        elif action == 'delete':
            worker_id = request.POST.get('worker_id')
            worker = get_object_or_404(WorkerProfile, pk=worker_id)
            worker.delete()
            return JsonResponse({'success': True})

        elif action == 'assign_skills':
            worker_id = request.POST.get('worker_id')
            worker = get_object_or_404(WorkerProfile, pk=worker_id)
            skills = request.POST.get('skills', '[]')
            try:
                worker.skills = json.loads(skills)
                worker.save()
                return JsonResponse({'success': True})
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'فرمت JSON نامعتبر'})

        elif action == 'assign_excluded_products':
            worker_id = request.POST.get('worker_id')
            product_ids = request.POST.get('excluded_products', '')
            worker = get_object_or_404(WorkerProfile, pk=worker_id)
            try:
                ids = [int(x) for x in product_ids.split(',') if x.strip()]
                worker.excluded_products.set(ids)
                return JsonResponse({'success': True})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'داده‌های نامعتبر'})

        elif action == 'assign_excluded_items':
            worker_id = request.POST.get('worker_id')
            worker = get_object_or_404(WorkerProfile, pk=worker_id)
            item_ids = request.POST.getlist('excluded_items')
            try:
                item_ids = [int(iid) for iid in item_ids if iid]
                worker.excluded_items.set(item_ids)
                return JsonResponse({'success': True, 'message': 'آیتم‌های ممنوعه ذخیره شدند.'})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'شناسه‌های آیتم نامعتبر'})

    workers = WorkerProfile.objects.filter(stage='paint').select_related('user').annotate(
        active_tasks=Count(
            'user__assigned_tasks',
            filter=Q(user__assigned_tasks__station_name='paint', user__assigned_tasks__status__in=['pending', 'waiting'])
        )
    ).order_by('user__username')

    search = request.GET.get('search')
    status = request.GET.get('status', '')
    skill_filter = request.GET.get('skill', '')
    if search:
        workers = workers.filter(
            Q(user__username__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
        )
    if status:
        if status == 'active':
            workers = workers.filter(is_available=True)
        elif status == 'inactive':
            workers = workers.filter(is_available=False)
    if skill_filter:
        workers = workers.filter(skills__contains=[skill_filter])

    paginator = Paginator(workers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    all_products = Product.objects.select_related('category').order_by('category__name', 'name')

    context = {
        'active_tab': 'workers',
        'workers': page_obj,
        'search': search,
        'status': status,
        'skill_filter': skill_filter,
        'form': WorkerProfileForm(),
        'skill_choices': PaintingStage.SKILL_CHOICES,
        'all_products': all_products,
        'all_items': OrderItem.objects.select_related('product', 'order').filter(
            order__status__in=['planned', 'producing']
        ).order_by('-order__id'),
        'user_list': User.objects.filter(is_active=True).order_by('username'),
        **painting_nav_context(),
    }
    return render(request, 'production/painting_management/workers.html', context)


# === CHUNK 10 END ===


@login_required
@admin_or_manager_required
def painting_worker_excluded_items(request, worker_id):
    worker = get_object_or_404(WorkerProfile, pk=worker_id, stage='paint')
    excluded_products = worker.excluded_products.all()

    direct_excluded_items = list(worker.excluded_items.all())

    direct_ids = {x.id for x in direct_excluded_items}

    product_excluded_items = list(
        OrderItem.objects.filter(
            product__in=excluded_products,
            order__status__in=['planned', 'producing'],
        ).exclude(pk__in=direct_ids).select_related('order', 'product', 'order__customer')
    )

    for x in direct_excluded_items:
        x.ban_reason = 'item'
    for x in product_excluded_items:
        x.ban_reason = 'product'

    combined = direct_excluded_items + product_excluded_items
    combined.sort(key=lambda x: getattr(x, 'order_id', 0) or 0, reverse=True)

    page_number = request.GET.get('page')
    paginator = Paginator(combined, 50)
    excluded_items_page = paginator.get_page(page_number)

    context = {
        'worker': worker,
        'excluded_products': excluded_products,
        'excluded_items': excluded_items_page,
        'excluded_count': len(combined),
        'direct_count': len(direct_excluded_items),
        'product_count': len(product_excluded_items),
        **painting_nav_context(),
    }
    return render(request, 'production/painting_management/worker_excluded_items.html', context)


@login_required
@admin_or_manager_required
def painting_schedule_view(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = parse_jalali_date(date_str)
        except ValueError:
            selected_date = jdatetime.date.today()
    else:
        selected_date = jdatetime.date.today()

    gregorian_date = selected_date.togregorian()

    tasks = list(
        ProductionTask.objects.filter(
            station_name='paint',
            scheduled_start__date=gregorian_date,
            part__isnull=True,
        ).select_related(
            'order_item__order', 'order_item__product', 'order_item__product__category',
            'painting_stage', 'assigned_worker',
        ).prefetch_related('order_item__ordercolor').order_by('scheduled_start', 'step_order')
    )

    workers = list(WorkerProfile.objects.filter(stage='paint', is_available=True).select_related('user'))

    tasks_by_worker = {}
    for t in tasks:
        tasks_by_worker.setdefault(t.assigned_worker_id, []).append(t)

    unscheduled_tasks = list(
        ProductionTask.objects.filter(
            station_name='paint',
            scheduled_start__isnull=True,
            status__in=['pending', 'waiting'],
            part__isnull=True,
        ).select_related(
            'order_item__order', 'order_item__product', 'order_item__product__category',
            'painting_stage', 'assigned_worker',
        ).prefetch_related('order_item__ordercolor').order_by('step_order')
    )

    worker_columns = [{
        'worker_id': '__unscheduled__',
        'label': 'بدون برنامه‌ریزی',
        'skills': [],
        'tasks': unscheduled_tasks,
        'is_unscheduled': True,
    }] + [{
        'worker_id': wp.user_id,
        'label': wp.user.get_full_name() or wp.user.username,
        'skills': wp.skills or [],
        'tasks': tasks_by_worker.get(wp.user_id, []),
    } for wp in workers]

    unassigned_tasks = tasks_by_worker.get(None, [])
    ready_unscheduled = get_unscheduled_ready_items()

    stats = {
        'total_tasks': len(tasks),
        'assigned_tasks': sum(1 for t in tasks if t.assigned_worker_id),
        'unassigned_tasks': len(unassigned_tasks),
        'ready_unscheduled': ready_unscheduled.count(),
        'total_duration': sum(t.painting_stage.duration_minutes if t.painting_stage else 0 for t in tasks),
    }

    context = {
        'active_tab': 'schedule',
        'worker_columns': worker_columns,
        'unassigned_tasks': unassigned_tasks,
        'ready_unscheduled': ready_unscheduled,
        'selected_date': selected_date,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'stats': stats,
        'yesterday': (selected_date - jdatetime.timedelta(days=1)).strftime('%Y-%m-%d'),
        'tomorrow': (selected_date + jdatetime.timedelta(days=1)).strftime('%Y-%m-%d'),
        'schedule_date': selected_date.strftime('%Y-%m-%d'),
        **painting_nav_context(),
    }
    return render(request, 'production/painting_management/schedule.html', context)


@login_required
@admin_or_manager_required
def painting_ready_list_view(request):
    search = request.GET.get('search', '')
    process_id = request.GET.get('process')

    ready_items = get_painting_ready_items_queryset(search=search, process_id=process_id)

    items_with_preview = [
        {'item': item, 'preview': get_item_paint_preview(item)}
        for item in ready_items
    ]

    context = {
        'active_tab': 'ready',
        'items_with_preview': items_with_preview,
        'search': search,
        'processes': PaintingProcess.objects.filter(is_active=True),
        'selected_process': process_id,
        'schedule_date': jdatetime.date.today().strftime('%Y-%m-%d'),
        **painting_nav_context(),
    }
    return render(request, 'production/painting_management/ready_list.html', context)


# urls.py references `painting_ready_list`; alias kept for legacy compatibility.
painting_ready_list = painting_ready_list_view


@login_required
@admin_or_manager_required
def painting_add_to_schedule(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})

    item_ids_raw = request.POST.getlist('item_ids[]') or request.POST.getlist('item_ids')
    if not item_ids_raw:
        return JsonResponse({'success': False, 'error': 'هیچ آیتمی انتخاب نشده است'})

    item_ids = []
    for val in item_ids_raw:
        try:
            item_ids.append(int(val))
        except (ValueError, TypeError):
            continue

    if not item_ids:
        return JsonResponse({'success': False, 'error': 'شناسه‌های آیتم نامعتبر هستند'})

    date_str = request.POST.get('date') or request.POST.get('target_date')
    target_date = None

    if date_str:
        try:
            target_date = parse_jalali_date(date_str)
        except Exception as e:
            logger.error(f"خطا در parse_jalali_date: {e}")
            target_date = jdatetime.date.today()
    else:
        target_date = jdatetime.date.today()

    if not isinstance(target_date, jdatetime.date):
        logger.warning(f"target_date از نوع {type(target_date)} است، جایگزین با امروز")
        target_date = jdatetime.date.today()

    try:
        result = create_and_schedule_items_for_date(item_ids, target_date)
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"خطا در create_and_schedule_items_for_date: {e}\n{error_trace}")
        return JsonResponse({
            'success': False,
            'error': f'خطای داخلی: {str(e)}',
        })

    created_count = len(result.get('created_items') or [])
    scheduled_count = result.get('scheduled_count') or 0
    scheduled_date = result.get('scheduled_date') or target_date
    skipped = result.get('skipped') or []

    if created_count == 0 and scheduled_count == 0 and not skipped:
        return JsonResponse({
            'success': False,
            'error': 'هیچ عملیاتی انجام نشد. احتمالاً آیتم‌ها قبلاً تسک دارند یا رنگ معتبری ندارند.'
        })

    if scheduled_count > 0:
        try:
            auto_assign_paint_tasks(target_date=scheduled_date)
        except Exception as e:
            logger.error(f"خطا در auto_assign_paint_tasks: {e}")

    message_parts = []
    if created_count:
        message_parts.append(f"{created_count} آیتم تسک جدید ایجاد شد")
    if scheduled_count:
        message_parts.append(f"{scheduled_count} تسک زمان‌بندی شد")
    if skipped:
        reasons = {'no_color': 'بدون رنگ', 'no_process_match': 'روند نقاشی یافت نشد'}
        detail = '؛ '.join(f"آیتم {s['item_id']}: {reasons.get(s['reason'], 'نامشخص')}" for s in skipped[:3])
        if len(skipped) > 3:
            detail += f' و {len(skipped) - 3} مورد دیگر'
        message_parts.append(f"{len(skipped)} آیتم رد شد ({detail})")

    message = ' + '.join(message_parts) if message_parts else 'همه آیتم‌ها قبلاً برنامه‌ریزی شده بودند.'

    return JsonResponse({
        'success': True,
        'message': message,
        'redirect': reverse('painting_schedule') + f'?date={scheduled_date.strftime("%Y-%m-%d")}',
    })


@login_required
@admin_or_manager_required
def painting_assign_process(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        item_id = request.POST.get('item_id')

        if not item_id:
            return JsonResponse({'success': False, 'error': 'اطلاعات ناقص'})

        item = get_object_or_404(OrderItem, pk=item_id)

        try:
            with transaction.atomic():
                existing = ProductionTask.objects.filter(order=item.order, station_name='paint', order_item=item)
                if existing.filter(status='done').exists():
                    return JsonResponse({'success': False, 'error': 'برخی مراحل قبلاً انجام شده‌اند؛ امکان بازسازی خودکار نیست.'})
                existing.delete()

                global_base = ProductionTask.objects.filter(order=item.order).aggregate(
                    max_step=models.Max('step_order')
                )['max_step'] or 0

                assignments = get_item_color_assignments(item)
                new_tasks = []

                for part_name, color_code in assignments:
                    painting_process = get_painting_process_for_color(color_code)
                    if not painting_process:
                        continue

                    create_paint_tasks(
                        new_tasks, item.order, item.quantity,
                        painting_process, global_base, order_item=item, color_part=part_name
                    )
                    global_base += painting_process.stages.count()

                if new_tasks:
                    ProductionTask.objects.bulk_create(new_tasks)

                return JsonResponse({'success': True, 'message': 'روند نقاشی با موفقیت اعمال شد.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})


@login_required
@admin_or_manager_required
def painting_auto_assign(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            target_date = None
            if request.POST.get('date'):
                target_date = parse_jalali_date(request.POST.get('date'))

            assigned_count = auto_assign_paint_tasks(target_date=target_date)

            return JsonResponse({
                'success': True,
                'message': 'تخصیص خودکار با موفقیت انجام شد.',
                'assigned_count': assigned_count or 0,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})


@login_required
@admin_or_manager_required
def painting_get_available_workers(request):
    skill = request.GET.get('skill')
    if not skill:
        return JsonResponse({'workers': []})

    workers = WorkerProfile.objects.filter(stage='paint').select_related('user')
    data = [{
        'id': w.user.id,
        'name': w.user.get_full_name() or w.user.username,
        'active_tasks': w.user.assigned_tasks.filter(status__in=['pending', 'waiting']).count()
    } for w in workers if skill in (w.skills or [])]

    return JsonResponse({'workers': data})


@login_required
@admin_or_manager_required
def painting_assign_worker(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})

    task_id = request.POST.get('task_id')
    worker_id = request.POST.get('worker_id')
    target_date = request.POST.get('target_date')
    allow_overtime = request.POST.get('allow_overtime') == 'true'

    if not task_id or not worker_id:
        return JsonResponse({'success': False, 'error': 'اطلاعات ناقص (task_id یا worker_id ارسال نشده)'})

    try:
        result = assign_task_to_worker(task_id, worker_id, target_date=target_date, allow_overtime=allow_overtime)

        if result.get('ok'):
            return JsonResponse({
                'success': True,
                'message': f"تسک به کارگر تخصیص یافت ({result.get('scheduled_start')} تا {result.get('scheduled_end')})",
                'scheduled_start': result.get('scheduled_start'),
                'scheduled_end': result.get('scheduled_end'),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'خطای ناشناخته'),
                'requires_overtime_confirmation': result.get('requires_overtime_confirmation', False),
            })

    except Exception as e:
        logger.error(f"خطا در painting_assign_worker: {e}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': f'خطای داخلی: {str(e)}'
        })


@login_required
@admin_or_manager_required
def painting_unassign_worker(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        task_id = request.POST.get('task_id')
        if not task_id:
            return JsonResponse({'success': False, 'error': 'اطلاعات ناقص'})
        task = get_object_or_404(ProductionTask, pk=task_id, station_name='paint')
        old_worker_id = task.assigned_worker_id
        old_scheduled_start = task.scheduled_start
        target_date = None
        if old_scheduled_start:
            try:
                target_date = jdatetime.date.fromgregorian(date=old_scheduled_start.date())
            except Exception:
                target_date = None
        task.assigned_worker = None
        task.scheduled_start = None
        task.scheduled_end = None
        task.save()

        if old_worker_id and target_date:
            try:
                reschedule_worker_tasks_on_date(old_worker_id, target_date)
            except Exception as e:
                logger.warning(f"خطا در بازنشانی تسک‌های کارگر {old_worker_id} در تاریخ {target_date}: {e}")

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})


@login_required
@admin_or_manager_required
def painting_delete_tasks(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})

    task_ids = request.POST.getlist('task_ids[]') or request.POST.getlist('task_ids')
    item_ids = request.POST.getlist('item_ids[]') or request.POST.getlist('item_ids')

    if not task_ids and not item_ids:
        return JsonResponse({'success': False, 'error': 'هیچ موردی انتخاب نشده است'})

    qs = ProductionTask.objects.filter(station_name='paint', status__in=['pending', 'waiting'])
    if item_ids:
        try:
            item_ids = [int(i) for i in item_ids]
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'شناسه‌های آیتم نامعتبر'})
        qs = qs.filter(order_item_id__in=item_ids)
    else:
        try:
            task_ids = [int(t) for t in task_ids]
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'شناسه‌های نامعتبر'})
        qs = qs.filter(pk__in=task_ids)

    deleted = qs.delete()[0]

    return JsonResponse({
        'success': True,
        'message': f'{deleted} تسک نقاشی حذف شد.',
        'deleted_count': deleted,
    })


@login_required
@admin_or_manager_required
def painting_clear_schedule(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})

    date_str = request.POST.get('date')
    if not date_str:
        return JsonResponse({'success': False, 'error': 'تاریخ ارسال نشده'})

    try:
        target_date = parse_jalali_date(date_str)
    except ValueError as exc:
        return JsonResponse({'success': False, 'error': str(exc)})

    gregorian = target_date.togregorian()
    tasks = ProductionTask.objects.filter(
        station_name='paint',
        scheduled_start__date=gregorian,
    )
    count = tasks.count()
    tasks.update(scheduled_start=None, scheduled_end=None, assigned_worker=None)
    return JsonResponse({
        'success': True,
        'message': f'{count} تسک از برنامه {target_date.strftime("%Y/%m/%d")} حذف شد.',
        'cleared_count': count,
    })


@login_required
@admin_or_manager_required
def painting_reset_schedule(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})

    date_str = request.POST.get('date')
    if not date_str:
        return JsonResponse({'success': False, 'error': 'تاریخ ارسال نشده'})

    try:
        target_date = parse_jalali_date(date_str)
    except ValueError as exc:
        return JsonResponse({'success': False, 'error': str(exc)})

    gregorian = target_date.togregorian()

    tasks = ProductionTask.objects.filter(
        station_name='paint',
        scheduled_start__date=gregorian,
        status__in=['pending', 'waiting'],
    )
    unassigned_count = tasks.count()
    tasks.update(assigned_worker=None, scheduled_start=None, scheduled_end=None)

    try:
        assigned_count = auto_assign_paint_tasks(target_date=target_date)
    except Exception as exc:
        logger.error(f"خطا در painting_reset_schedule: {exc}\n{traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': f'خطا در بازنشانی: {str(exc)}'})

    remaining_unassigned = ProductionTask.objects.filter(
        station_name='paint',
        scheduled_start__date=gregorian,
        status__in=['pending', 'waiting'],
        assigned_worker__isnull=True,
    ).count()

    message = (
        f'زمان‌بندی بازنشانی شد. '
        f'{unassigned_count} تسک آزاد، {assigned_count} تسک مجدداً تخصیص داده شد. '
        f'{remaining_unassigned} تسک به دلیل نبود ظرفیت یا عدم تأیید skill باقی ماند.'
    )
    return JsonResponse({
        'success': True,
        'message': message,
        'unassigned_count': unassigned_count,
        'assigned_count': assigned_count,
        'remaining_unassigned': remaining_unassigned,
    })


@login_required
@admin_or_manager_required
def painting_repaint_items(request):
    if request.method != 'POST' or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})

    item_ids = request.POST.getlist('item_ids[]') or request.POST.getlist('item_ids')
    date_str = request.POST.get('date')

    if not item_ids:
        return JsonResponse({'success': False, 'error': 'هیچ آیتمی انتخاب نشده است'})

    if not date_str:
        return JsonResponse({'success': False, 'error': 'تاریخ ارسال نشده'})

    try:
        target_date = parse_jalali_date(date_str)
    except ValueError as exc:
        return JsonResponse({'success': False, 'error': str(exc)})

    try:
        result = repaint_item_ids_for_date(item_ids, target_date)
        return JsonResponse({
            'success': True,
            'message': f'برنامه‌ریزی مجدد انجام شد. {result.get("scheduled_count", 0)} تسک زمان‌بندی شد.',
            'result': result,
            'redirect': reverse('painting_schedule') + f'?date={target_date.strftime("%Y-%m-%d")}',
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@admin_or_manager_required
def painting_assignment_rules_view(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')

        if action == 'create':
            worker_id = request.POST.get('worker')
            stage_id = request.POST.get('stage') or None
            process_id = request.POST.get('process') or None
            color_codes_str = request.POST.get('color_codes', '')
            rule_type = request.POST.get('rule_type', 'priority')
            is_active = request.POST.get('is_active', 'true') == 'true'

            if not worker_id:
                return JsonResponse({'success': False, 'error': 'کارگر الزامی است'})

            worker = get_object_or_404(WorkerProfile, pk=worker_id, stage='paint')
            stage = get_object_or_404(PaintingStage, pk=stage_id) if stage_id else None
            process = get_object_or_404(PaintingProcess, pk=process_id) if process_id else None

            color_codes = [c.strip() for c in color_codes_str.split(',') if c.strip()] if color_codes_str else None

            rule = PaintingAssignmentRule.objects.create(
                worker=worker,
                painting_stage=stage,
                process=process,
                color_codes=color_codes,
                rule_type=rule_type,
                priority=100,
                is_active=is_active,
            )
            return JsonResponse({'success': True, 'id': rule.id})

        elif action == 'edit':
            rule_id = request.POST.get('rule_id')
            rule = get_object_or_404(PaintingAssignmentRule, pk=rule_id)

            worker_id = request.POST.get('worker')
            stage_id = request.POST.get('stage') or None
            process_id = request.POST.get('process') or None
            color_codes_str = request.POST.get('color_codes', '')
            rule_type = request.POST.get('rule_type', rule.rule_type)
            is_active = request.POST.get('is_active', 'true') == 'true'

            if worker_id:
                rule.worker = get_object_or_404(WorkerProfile, pk=worker_id, stage='paint')
            if stage_id:
                rule.painting_stage = get_object_or_404(PaintingStage, pk=stage_id)
            else:
                rule.painting_stage = None
            if process_id:
                rule.process = get_object_or_404(PaintingProcess, pk=process_id)
            else:
                rule.process = None

            rule.color_codes = [c.strip() for c in color_codes_str.split(',') if c.strip()] if color_codes_str else None
            rule.rule_type = rule_type
            rule.is_active = is_active
            rule.save()
            return JsonResponse({'success': True})

        elif action == 'delete':
            rule_id = request.POST.get('rule_id')
            rule = get_object_or_404(PaintingAssignmentRule, pk=rule_id)
            rule.delete()
            return JsonResponse({'success': True})

        elif action == 'toggle_active':
            rule_id = request.POST.get('rule_id')
            rule = get_object_or_404(PaintingAssignmentRule, pk=rule_id)
            rule.is_active = not rule.is_active
            rule.save()
            return JsonResponse({'success': True, 'is_active': rule.is_active})

        return JsonResponse({'success': False, 'error': 'عملیات نامعتبر'})

    rules = PaintingAssignmentRule.objects.select_related(
        'worker__user', 'painting_stage', 'painting_stage__process', 'process'
    ).order_by('-priority')

    context = {
        'active_tab': 'assignment_rules',
        'rules': rules,
        'workers': WorkerProfile.objects.filter(stage='paint', is_available=True).select_related('user'),
        'stages': PaintingStage.objects.all().select_related('process'),
        'processes': PaintingProcess.objects.filter(is_active=True),
        **painting_nav_context(),
    }
    return render(request, 'production/painting_management/assignment_rules.html', context)


@login_required
@admin_or_manager_required
def delete_all_tasks(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    done_tasks = order.tasks.filter(status='done')
    if done_tasks.exists():
        messages.warning(request, f"{done_tasks.count()} تسک قبلاً تکمیل شده‌اند. با حذف آن‌ها، سابقه از بین می‌رود.")

    with transaction.atomic():
        order.tasks.all().delete()
        order.status = 'draft'
        order.save(update_fields=['status'])

    messages.success(request, f"✅ تمام تسک‌های سفارش {order.id} حذف شدند و وضعیت به پیش‌نویس برگردانده شد.")
    return redirect('order_detail', order_id=order.id)


@login_required
@admin_or_manager_required
def delete_paint_tasks(request, item_id):
    item = get_object_or_404(OrderItem, pk=item_id)

    paint_tasks = item.paint_tasks.all()
    count = paint_tasks.count()
    if count == 0:
        messages.warning(request, "هیچ تسک نقاشی‌ای برای این آیتم وجود ندارد.")
        return redirect('item_detail', pk=item.id)

    done_tasks = paint_tasks.filter(status='done')
    if done_tasks.exists():
        messages.warning(request, f"{done_tasks.count()} تسک نقاشی قبلاً تکمیل شده‌اند. با حذف آن‌ها، سابقه از بین می‌رود.")

    with transaction.atomic():
        paint_tasks.delete()

    messages.success(request, f"✅ {count} تسک نقاشی آیتم {item.id} حذف شدند.")
    return redirect('item_detail', pk=item.id)


@login_required
@admin_or_manager_required
def delete_all_paint_tasks_for_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    paint_tasks = order.tasks.filter(station_name='paint')
    count = paint_tasks.count()
    if count == 0:
        messages.warning(request, "هیچ تسک نقاشی‌ای برای این سفارش وجود ندارد.")
        return redirect('order_detail', order_id=order.id)

    done_tasks = paint_tasks.filter(status='done')
    if done_tasks.exists():
        messages.warning(request, f"{done_tasks.count()} تسک نقاشی قبلاً تکمیل شده‌اند. با حذف آن‌ها، سابقه از بین می‌رود.")

    with transaction.atomic():
        paint_tasks.delete()
        remaining_tasks = order.tasks.exclude(station_name='paint')
        if not remaining_tasks.exists():
            order.status = 'draft'
            order.save(update_fields=['status'])

    messages.success(request, f"✅ {count} تسک نقاشی سفارش {order.id} حذف شدند.")
    return redirect('order_detail', order_id=order.id)


# === MIGRATED VIEWS END ===

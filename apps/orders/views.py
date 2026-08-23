from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from apps.cart.models import Cart
from apps.production.views import ProductionTask
from apps.common.permissions import is_production_staff
from .models import Order, OrderItem, Customer, PackagingUnit, ShipmentLog, Address, ReturnRequest
from .forms import OrderForm
from .services import validate_cart_stock, InsufficientStockError, OrderService


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        try:
            validate_cart_stock(request.user)
        except InsufficientStockError as e:
            messages.error(request, str(e))
            return redirect('cart:cart_detail')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['addresses'] = Address.objects.filter(user=self.request.user)
        else:
            context['addresses'] = Address.objects.none()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        customer, _ = Customer.objects.get_or_create(
            user=self.request.user,
            defaults={
                'name': self.request.user.get_full_name() or self.request.user.username,
                'phone': getattr(self.request.user, 'phone', '') or '',
            }
        )
        form.instance.customer = customer

        address_id = self.request.POST.get('address_id')
        if address_id:
            try:
                address = Address.objects.get(id=address_id, user=self.request.user)
                form.instance.address = address
                form.instance.shipping_address = f"{address.recipient}\n{address.province} {address.city}\n{address.address}\nکد پستی: {address.postal_code}"
            except Address.DoesNotExist:
                pass

        response = super().form_valid(form)
        cart = get_object_or_404(Cart, user=self.request.user)
        OrderService.add_cart_items_to_order(self.object, cart)
        return redirect('orders:order_confirm', order_id=self.object.id)


class OrderDetailView(LoginRequiredMixin, ListView):
    model = OrderItem
    template_name = 'orders/order_detail.html'
    context_object_name = 'items'

    def get_queryset(self):
        return OrderItem.objects.filter(order_id=self.kwargs['order_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, id=self.kwargs['order_id'], user=self.request.user)
        context['production_staff'] = is_production_staff(self.request.user)
        return context


class OrderCancelView(LoginRequiredMixin, View):
    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status in ('draft', 'planned'):
            order.status = 'cancelled'
            order.save(update_fields=['status'])
            messages.success(request, 'سفارش شما با موفقیت لغو شد.')
        else:
            messages.error(request, 'امکان لغو سفارش در این وضعیت وجود ندارد.')
        return redirect('orders:order_detail', order_id=order.id)


class PackagingMarkPackedView(LoginRequiredMixin, View):
    def post(self, request, unit_id, *args, **kwargs):
        if not is_production_staff(request.user):
            messages.error(request, 'دسترسی مجاز نیست.')
            return redirect('home')
        unit = get_object_or_404(PackagingUnit, id=unit_id)
        if not unit.is_packed:
            unit.is_packed = True
            unit.packed_at = timezone.now()
            unit.packed_by = request.user
            unit.save(update_fields=['is_packed', 'packed_at', 'packed_by'])
            messages.success(request, f'واحد {unit.unit_number} بسته‌بندی شد.')
        else:
            messages.info(request, 'این واحد قبلاً بسته‌بندی شده است.')
        return redirect('orders:order_detail', order_id=unit.order_item.order_id)


class PackagingMarkShippedView(LoginRequiredMixin, View):
    def post(self, request, unit_id, *args, **kwargs):
        if not is_production_staff(request.user):
            messages.error(request, 'دسترسی مجاز نیست.')
            return redirect('home')
        unit = get_object_or_404(PackagingUnit, id=unit_id)
        if not unit.is_packed:
            messages.error(request, 'قبل از ارسال باید بسته‌بندی شود.')
            return redirect('orders:order_detail', order_id=unit.order_item.order_id)
        plate_number = request.POST.get('plate_number', '').strip()
        if not unit.is_shipped:
            unit.is_shipped = True
            unit.shipped_at = timezone.now()
            unit.shipped_by = request.user
            unit.save(update_fields=['is_shipped', 'shipped_at', 'shipped_by'])
            ShipmentLog.objects.create(
                packaging_unit=unit,
                plate_number=plate_number,
                shipped_by=request.user,
            )
            messages.success(request, f'واحد {unit.unit_number} ارسال شد.')
        else:
            messages.info(request, 'این واحد قبلاً ارسال شده است.')
        return redirect('orders:order_detail', order_id=unit.order_item.order_id)


class OrderConfirmView(LoginRequiredMixin, ListView):
    model = OrderItem
    template_name = 'orders/order_confirm.html'
    context_object_name = 'items'

    def get_queryset(self):
        return OrderItem.objects.filter(order_id=self.kwargs['order_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, id=self.kwargs['order_id'], user=self.request.user)
        return context


class ReturnRequestCreateView(LoginRequiredMixin, CreateView):
    model = ReturnRequest
    fields = ['reason']
    template_name = 'orders/return_request_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_item'] = get_object_or_404(OrderItem, id=self.kwargs['item_id'], order__user=self.request.user)
        return context

    def form_valid(self, form):
        order_item = get_object_or_404(OrderItem, id=self.kwargs['item_id'], order__user=self.request.user)
        form.instance.order_item = order_item
        form.instance.user = self.request.user
        messages.success(self.request, 'درخواست مرجوعی شما ثبت شد.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'order_id': self.object.order_item.order_id})


class ReturnRequestListView(LoginRequiredMixin, ListView):
    model = ReturnRequest
    template_name = 'orders/return_request_list.html'
    context_object_name = 'return_requests'

    def get_queryset(self):
        qs = ReturnRequest.objects.all().select_related('order_item__product', 'user')
        if not is_production_staff(self.request.user):
            qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_production_staff'] = is_production_staff(self.request.user)
        return context


class ReturnRequestDetailView(LoginRequiredMixin, DetailView):
    model = ReturnRequest
    template_name = 'orders/return_request_detail.html'
    context_object_name = 'return_request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_production_staff'] = is_production_staff(self.request.user)
        return context


class ReturnRequestProcessView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if not is_production_staff(request.user):
            messages.error(request, 'دسترسی مجاز نیست.')
            return redirect('home')
        
        return_request = get_object_or_404(ReturnRequest, pk=pk)
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '').strip()
        
        if action == 'approve':
            return_request.approve(admin_note)
            messages.success(request, 'درخواست مرجوعی تایید شد.')
        elif action == 'reject':
            return_request.reject(admin_note)
            messages.success(request, 'درخواست مرجوعی رد شد.')
        elif action == 'refund':
            return_request.refund()
            messages.success(request, 'بازپرداخت انجام شد.')
        
        return redirect('orders:return_request_detail', pk=return_request.id)

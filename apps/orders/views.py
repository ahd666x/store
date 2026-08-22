from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.contrib import messages
from apps.cart.models import Cart
from .models import Order, OrderItem, Customer
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
        try:
            validate_cart_stock(request.user)
        except InsufficientStockError as e:
            messages.error(request, str(e))
            return redirect('cart:cart_detail')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        customer, _ = Customer.objects.get_or_create(
            user=self.request.user,
            defaults={
                'name': self.request.user.get_full_name() or self.request.user.username,
                'phone': getattr(self.request.user, 'phone', ''),
            }
        )
        form.instance.customer = customer
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
        return context


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

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Order, OrderItem
from .forms import OrderForm


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
    success_url = reverse_lazy('orders:order_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


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

from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Discount
from .forms import DiscountForm


class DiscountListView(LoginRequiredMixin, ListView):
    model = Discount
    template_name = 'discounts/discount_list.html'
    context_object_name = 'discounts'


class DiscountCreateView(LoginRequiredMixin, CreateView):
    model = Discount
    form_class = DiscountForm
    template_name = 'discounts/discount_form.html'
    success_url = reverse_lazy('discounts:discount_list')


class DiscountUpdateView(LoginRequiredMixin, UpdateView):
    model = Discount
    form_class = DiscountForm
    template_name = 'discounts/discount_form.html'
    success_url = reverse_lazy('discounts:discount_list')

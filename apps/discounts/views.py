from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import Discount
from .forms import DiscountForm, ApplyDiscountForm
from apps.cart.models import Cart


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


class ApplyDiscountView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        form = ApplyDiscountForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                discount = Discount.objects.get(code=code)
            except Discount.DoesNotExist:
                messages.error(request, 'کد تخفیف نامعتبر است.')
                return redirect('cart:cart_detail')

            if not discount.is_valid:
                messages.error(request, 'کد تخفیف منقضی شده یا به حد نصاب رسیده است.')
                return redirect('cart:cart_detail')

            cart.discount = discount
            cart.save()
            messages.success(request, f'کد تخفیف {discount.code} با موفقیت اعمال شد.')
        return redirect('cart:cart_detail')


class RemoveDiscountView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.discount = None
        cart.save()
        messages.success(request, 'کد تخفیف حذف شد.')
        return redirect('cart:cart_detail')

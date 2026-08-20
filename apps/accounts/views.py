from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from apps.catalog.models import Product


def home(request):
    featured_products = Product.objects.filter(is_active=True, stock__gt=0).order_by('-created_at')[:8]
    return render(request, 'home.html', {'featured_products': featured_products})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = 'accounts:login'

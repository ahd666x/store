from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.catalog.models import Product
from .models import User, OTPCode
from .forms import UserRegistrationForm


def home(request):
    featured_products = Product.objects.filter(is_active=True, stock__gt=0).order_by('-created_at')[:8]
    return render(request, 'home.html', {'featured_products': featured_products})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = 'accounts:login'


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class ProfileView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'accounts/profile.html'
    context_object_name = 'orders'

    def get_queryset(self):
        from apps.orders.models import Order
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OTPRequestView(CreateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/otp_request.html')

    def post(self, request, *args, **kwargs):
        phone = request.POST.get('phone', '').strip()
        if not phone:
            messages.error(request, 'شماره موبایل الزامی است.')
            return redirect('accounts:login')

        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={'username': phone, 'is_active': True}
        )

        code = OTPCode.objects.create(
            user=user,
            phone=phone,
            code=OTPCode.generate_code(),
            expires_at=timezone.now() + timezone.timedelta(minutes=5),
        )

        messages.success(request, f'کد تایید: {code.code} (در سیستم واقعی این کد به شماره {phone} ارسال می‌شود)')

        request.session['otp_phone'] = phone
        return redirect('accounts:otp_verify')


class OTPVerifyView(CreateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/otp_verify.html')

    def post(self, request, *args, **kwargs):
        phone = request.session.get('otp_phone')
        code = request.POST.get('code', '').strip()

        if not phone or not code:
            messages.error(request, 'شماره موبایل و کد الزامی است.')
            return redirect('accounts:login')

        otp = OTPCode.objects.filter(phone=phone, code=code, is_used=False, expires_at__gte=timezone.now()).first()
        if not otp:
            messages.error(request, 'کد نامعتبر یا منقضی شده است.')
            return redirect('accounts:login')

        otp.is_used = True
        otp.save()

        user = otp.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        from django.contrib.auth import login
        login(request, user)

        messages.success(request, 'ورود با موفقیت انجام شد.')
        return redirect('home')

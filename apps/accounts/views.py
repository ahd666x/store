from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Avg, Count
from django.views.generic import CreateView, ListView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.catalog.models import Product
from apps.orders.models import Order
from .models import User, OTPCode, Wishlist, WishlistItem
from .forms import UserRegistrationForm, ProfileUpdateForm


def home(request):
    featured_products = Product.active_objects.filter(stock__gt=0).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
        rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
    ).order_by('-created_at')[:8]
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
    model = Order
    template_name = 'accounts/profile.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'پروفایل شما با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)


class WishlistView(LoginRequiredMixin, ListView):
    model = WishlistItem
    template_name = 'accounts/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist.items.select_related('product').prefetch_related('product__images')


class WishlistAddView(LoginRequiredMixin, View):
    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        _, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        if created:
            messages.success(request, 'محصول به علاقه‌مندی‌ها اضافه شد.')
        else:
            messages.info(request, 'این محصول قبلاً در لیست علاقه‌مندی‌ها وجود دارد.')
        return redirect('catalog:product_detail', slug=product.slug)


class WishlistRemoveView(LoginRequiredMixin, View):
    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
        messages.success(request, 'محصول از علاقه‌مندی‌ها حذف شد.')
        return redirect('accounts:wishlist')


class OTPRequestView(CreateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/otp_request.html')

    def post(self, request, *args, **kwargs):
        phone = request.POST.get('phone', '').strip()
        if not phone:
            messages.error(request, 'شماره موبایل الزامی است.')
            return redirect('accounts:login')

        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        recent_otps = OTPCode.objects.filter(phone=phone, created_at__gte=one_hour_ago)
        if recent_otps.count() >= 5:
            messages.error(request, 'تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً تلاش کنید.')
            return redirect('accounts:login')

        OTPCode.objects.filter(phone=phone, is_used=False, expires_at__gte=timezone.now()).update(is_used=True)

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

        messages.success(request, 'کد تایید به شماره موبایل شما ارسال شد.')

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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.db.models import Q, Min, Max, Avg, Count
from django.db import IntegrityError
from django.contrib import messages
from .models import Product, ProductCategory, ProductReview, StockAlert, ComparisonList


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.active_objects.filter().prefetch_related('images')

        # Search
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )

        # Filter by price range
        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()
        try:
            if min_price:
                queryset = queryset.filter(price__gte=int(min_price))
            if max_price:
                queryset = queryset.filter(price__lte=int(max_price))
        except (ValueError, TypeError):
            pass

        # Filter by category
        category_slug = self.request.GET.get('category', '').strip()
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by color
        color = self.request.GET.get('color', '').strip()
        if color:
            queryset = queryset.filter(color__iexact=color)

        # Annotate rating data to avoid N+1
        queryset = queryset.annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
            rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
        )

        # Sorting
        sort = self.request.GET.get('sort', '').strip()
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'rating' or sort == '-average_rating':
            queryset = queryset.order_by('-avg_rating')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_sort'] = self.request.GET.get('sort', '')
        context['selected_color'] = self.request.GET.get('color', '')
        context['categories'] = ProductCategory.objects.all()
        context['colors'] = Product.active_objects.exclude(color__isnull=True).exclude(color__exact='').values_list('color', flat=True).distinct().order_by('color')
        context['featured_products'] = Product.active_objects.filter(stock__gt=0).order_by('-created_at')[:8]
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.active_objects.filter().prefetch_related(
            'images',
        ).annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
            rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['reviews'] = ProductReview.objects.filter(product=product, is_active=True).select_related('user')
        context['can_review'] = False
        if self.request.user.is_authenticated:
            context['can_review'] = not ProductReview.objects.filter(product=product, user=self.request.user).exists()
        
        # Related products by category
        context['related_products'] = Product.active_objects.filter(
            category=product.category
        ).exclude(id=product.id).prefetch_related('images')[:4]
        
        # Smart recommendations based on cart/wishlist
        if self.request.user.is_authenticated:
            from apps.cart.models import Cart
            cart_product_ids = Cart.objects.filter(user=self.request.user).values_list('items__product_id', flat=True).distinct()
            wishlist_product_ids = self.request.user.wishlist.items.values_list('product_id', flat=True).distinct()
            product_ids = set(cart_product_ids) | set(wishlist_product_ids)
            
            if product_ids:
                context['recommended_products'] = Product.active_objects.filter(
                    category__in=Product.objects.filter(id__in=product_ids).values_list('category', flat=True).distinct()
                ).exclude(id__in=product_ids).exclude(id=product.id).prefetch_related('images').annotate(
                    avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
                    rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
                ).order_by('-avg_rating', '-created_at')[:8]
            else:
                context['recommended_products'] = Product.active_objects.filter(
                    category=product.category
                ).exclude(id=product.id).prefetch_related('images').annotate(
                    avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
                    rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
                ).order_by('-avg_rating')[:8]
        else:
            context['recommended_products'] = Product.active_objects.filter(
                category=product.category
            ).exclude(id=product.id).prefetch_related('images').annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
                rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
            ).order_by('-avg_rating')[:8]
        
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        product = self.get_object()
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            messages.error(request, 'شما قبلاً برای این محصول نظر ثبت کرده‌اید.')
            return redirect('catalog:product_detail', slug=product.slug)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        review_image = request.FILES.get('review_image')
        if rating and comment:
            try:
                review = ProductReview.objects.create(
                    product=product,
                    user=request.user,
                    rating=int(rating),
                    comment=comment,
                    image=review_image,
                )
                messages.success(request, 'نظر شما ثبت شد.')
            except IntegrityError:
                messages.error(request, 'شما قبلاً برای این محصول نظر ثبت کرده‌اید.')
        else:
            messages.error(request, 'امتیاز و متن نظر الزامی است.')
        return redirect('catalog:product_detail', slug=product.slug)


class CategoryListView(ListView):
    model = ProductCategory
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(ListView):
    model = Product
    template_name = 'catalog/category_detail.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.active_objects.filter(
            category__slug=self.kwargs['slug'],
        ).prefetch_related('images').annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
            rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(ProductCategory, slug=self.kwargs['slug'])
        return context


class ComparisonView(ListView):
    template_name = 'catalog/comparison.html'
    context_object_name = 'products'

    def get_queryset(self):
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        comparison = ComparisonList.objects.filter(session_key=session_key).first()
        if comparison:
            return comparison.products.prefetch_related('images')
        return Product.objects.none()


class ComparisonAddView(LoginRequiredMixin, View):
    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        comparison, _ = ComparisonList.objects.get_or_create(session_key=session_key)
        comparison.products.add(product)
        messages.success(request, 'محصول به لیست مقایسه اضافه شد.')
        return redirect('catalog:product_detail', slug=product.slug)


class ComparisonRemoveView(LoginRequiredMixin, View):
    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        session_key = request.session.session_key
        if session_key:
            comparison = ComparisonList.objects.filter(session_key=session_key).first()
            if comparison:
                comparison.products.remove(product)
        messages.success(request, 'محصول از لیست مقایسه حذف شد.')
        return redirect('catalog:comparison')


class ComparisonClearView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        session_key = request.session.session_key
        if session_key:
            ComparisonList.objects.filter(session_key=session_key).delete()
        messages.success(request, 'لیست مقایسه پاک شد.')
        return redirect('catalog:comparison')


class StockAlertCreateView(LoginRequiredMixin, View):
    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        alert, created = StockAlert.objects.get_or_create(user=request.user, product=product)
        if created:
            messages.success(request, 'هنگام موجود شدن این محصول به شما اطلاع داده می‌شود.')
        else:
            messages.info(request, 'شما قبلاً برای این محصول درخواست اطلاع داده‌اید.')
        return redirect('catalog:product_detail', slug=product.slug)


class StockAlertListView(LoginRequiredMixin, ListView):
    model = StockAlert
    template_name = 'catalog/stock_alerts.html'
    context_object_name = 'alerts'

    def get_queryset(self):
        return StockAlert.objects.filter(user=self.request.user).select_related('product')


class RecommendationsView(ListView):
    template_name = 'catalog/recommendations.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.active_objects.filter(stock__gt=0).none()
        user = self.request.user

        if user.is_authenticated:
            from apps.cart.models import Cart
            cart_product_ids = Cart.objects.filter(user=user).values_list('items__product_id', flat=True).distinct()
            wishlist_product_ids = user.wishlist.items.values_list('product_id', flat=True).distinct()
            product_ids = set(cart_product_ids) | set(wishlist_product_ids)

            if product_ids:
                queryset = Product.active_objects.filter(
                    category__in=Product.objects.filter(id__in=product_ids).values_list('category', flat=True).distinct()
                ).exclude(id__in=product_ids).prefetch_related('images').annotate(
                    avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
                    rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
                ).order_by('-avg_rating', '-created_at')[:12]

        return queryset

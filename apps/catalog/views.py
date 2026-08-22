from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Q, Min, Max, Avg, Count
from .models import Product, ProductCategory, ProductReview


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).prefetch_related('images', 'sections__pieces')

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
        context['categories'] = ProductCategory.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related(
            'images',
            'sections__color',
            'sections__pieces',
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
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        product = self.get_object()
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        if rating and comment:
            ProductReview.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                comment=comment,
            )
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
        return Product.objects.filter(
            category__slug=self.kwargs['slug'],
            is_active=True
        ).prefetch_related('images', 'sections__pieces').annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_active=True)),
            rev_count=Count('reviews', filter=Q(reviews__is_active=True)),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(ProductCategory, slug=self.kwargs['slug'])
        return context

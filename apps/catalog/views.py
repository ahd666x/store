from django.shortcuts import render
from apps.catalog.models import Product, ProductCategory
from django.views.generic import ListView, DetailView


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(is_active=True)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


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
        return Product.objects.filter(category__slug=self.kwargs['slug'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = ProductCategory.objects.get(slug=self.kwargs['slug'])
        return context

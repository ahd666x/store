from django.urls import path, register_converter
from apps.common.converters import UnicodeSlugConverter
from . import views

register_converter(UnicodeSlugConverter, 'uslug')

app_name = 'catalog'
urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<uslug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<uslug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
]

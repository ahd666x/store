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
    path('compare/', views.ComparisonView.as_view(), name='comparison'),
    path('compare/add/<int:product_id>/', views.ComparisonAddView.as_view(), name='comparison_add'),
    path('compare/remove/<int:product_id>/', views.ComparisonRemoveView.as_view(), name='comparison_remove'),
    path('compare/clear/', views.ComparisonClearView.as_view(), name='comparison_clear'),
    path('stock-alerts/', views.StockAlertListView.as_view(), name='stock_alerts'),
    path('stock-alert/add/<int:product_id>/', views.StockAlertCreateView.as_view(), name='stock_alert_add'),
]

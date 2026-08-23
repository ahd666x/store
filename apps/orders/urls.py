from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:order_id>/confirm/', views.OrderConfirmView.as_view(), name='order_confirm'),
    path('packaging/<int:unit_id>/pack/', views.PackagingMarkPackedView.as_view(), name='packaging_mark_packed'),
    path('packaging/<int:unit_id>/ship/', views.PackagingMarkShippedView.as_view(), name='packaging_mark_shipped'),
]

from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views

app_name = 'api'
urlpatterns = [
    path('', views.api_root, name='root'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/swagger/', SpectacularSwaggerView.as_view(url='/api/v1/schema/'), name='swagger-ui'),
    path('docs/redoc/', SpectacularRedocView.as_view(url='/api/v1/schema/'), name='redoc'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/users/me/', views.CurrentUserView.as_view({'get': 'list'}), name='current-user'),
    path('products/', views.ProductViewSet.as_view({'get': 'list'}), name='product-list'),
    path('products/<slug:slug>/', views.ProductViewSet.as_view({'get': 'retrieve'}), name='product-detail'),
    path('categories/', views.ProductCategoryViewSet.as_view({'get': 'list'}), name='category-list'),
    path('categories/<slug:slug>/', views.ProductCategoryViewSet.as_view({'get': 'retrieve'}), name='category-detail'),
    path('cart/', views.CartViewSet.as_view({'get': 'list'}), name='cart-detail'),
    path('cart/items/', views.CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('cart/items/remove/', views.CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove-item'),
    path('cart/discount/apply/', views.CartViewSet.as_view({'post': 'apply_discount'}), name='cart-apply-discount'),
    path('cart/discount/remove/', views.CartViewSet.as_view({'post': 'remove_discount'}), name='cart-remove-discount'),
    path('orders/', views.OrderViewSet.as_view({'get': 'list'}), name='order-list'),
    path('orders/<int:pk>/', views.OrderViewSet.as_view({'get': 'retrieve'}), name='order-detail'),
    path('orders/checkout/', views.OrderViewSet.as_view({'post': 'checkout'}), name='order-checkout'),
    path('discounts/', views.DiscountViewSet.as_view({'get': 'list'}), name='discount-list'),
    path('discounts/<int:pk>/', views.DiscountViewSet.as_view({'get': 'retrieve'}), name='discount-detail'),
]

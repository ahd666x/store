from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.catalog.models import Product, ProductCategory
from apps.orders.models import Order, ProductionTask
from apps.cart.models import Cart, CartItem
from apps.discounts.models import Discount
from .serializers import (
    ProductListSerializer,
    ProductSerializer,
    ProductCategorySerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    DiscountSerializer,
    UserSerializer,
    ProductionTaskSerializer,
)
from apps.orders.services import OrderService
from apps.cart.services import CartService


User = get_user_model()


def api_root(request, format=None):
    return Response({
        'products': '/api/v1/products/',
        'categories': '/api/v1/categories/',
        'cart': '/api/v1/cart/',
        'orders': '/api/v1/orders/',
        'discounts': '/api/v1/discounts/',
        'production_tasks': '/api/v1/production/tasks/',
        'token': '/api/v1/auth/token/',
        'docs': '/api/v1/docs/swagger/',
    })


class CurrentUserView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True, stock__gt=0)
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Cart, user=self.request.user)

    def list(self, request, *args, **kwargs):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)
        CartService.add_item(cart, product_id, quantity)
        return Response(self.get_serializer(cart).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        CartService.remove_item(cart, product_id)
        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=['post'])
    def apply_discount(self, request):
        cart = self.get_object()
        code = request.data.get('code', '').strip()
        if not code:
            return Response({'detail': 'code is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            discount = Discount.objects.get(code=code)
        except Discount.DoesNotExist:
            return Response({'detail': 'کد تخفیف نامعتبر است.'}, status=status.HTTP_404_NOT_FOUND)
        if not discount.is_valid:
            return Response({'detail': 'کد تخفیف منقضی شده یا به حد نصاب رسیده است.'}, status=status.HTTP_400_BAD_REQUEST)
        cart.discount = discount
        cart.save()
        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=['post'])
    def remove_discount(self, request):
        cart = self.get_object()
        cart.discount = None
        cart.save()
        return Response(self.get_serializer(cart).data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        shipping_address = request.data.get('shipping_address', '')
        if not shipping_address:
            return Response({'detail': 'shipping_address is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = OrderService.create_order_from_cart(request.user, shipping_address)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)


class DiscountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Discount.objects.filter(is_active=True)
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ProductionTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductionTask.objects.select_related('order', 'part', 'order_item', 'assigned_worker', 'scanned_by')
    serializer_class = ProductionTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        station = self.request.query_params.get('station')
        if station:
            qs = qs.filter(station_name=station)
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('order', 'step_order')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        if task.status == 'done':
            return Response({'detail': 'این تسک قبلا تکمیل شده است.'}, status=status.HTTP_400_BAD_REQUEST)
        task.status = 'done'
        task.scanned_by = request.user
        task.completed_at = timezone.now()
        task.save()
        return Response(ProductionTaskSerializer(task, context=self.get_serializer_context()).data)

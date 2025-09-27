from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, permissions
from django.db import models  # Added missing import

from .models import (
    CustomUser, Category, Product, ProductImage, ProductReview,
    Order, OrderItem, Wishlist, Payment, Cart, CartItem, ProductVariant
)
from .serializers import (
    UserSerializer, CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductImageSerializer, ProductReviewSerializer, OrderSerializer, OrderCreateSerializer,
    OrderItemSerializer, WishlistSerializer, WishlistCreateSerializer,
    PaymentSerializer, CartSerializer, CartItemSerializer, CartItemCreateSerializer,
    ProductVariantSerializer
)
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrAdmin
from .filters import ProductFilter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

# -------------------
# USER
# -------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

# -------------------
# CATEGORY
# -------------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminUserOrReadOnly]
    lookup_field = 'slug'

# -------------------
# PRODUCT
# -------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(status='active').prefetch_related(
        'variants', 'images', 'category'
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Custom ordering by price
        ordering = self.request.query_params.get('ordering')
        if ordering == 'price':
            queryset = queryset.annotate(
                min_price=models.Min('variants__price')
            ).order_by('min_price')
        elif ordering == '-price':
            queryset = queryset.annotate(
                max_price=models.Max('variants__price')
            ).order_by('-max_price')
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def variants(self, request, slug=None):
        """Get all variants for a product"""
        product = self.get_object()
        variants = product.variants.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminUserOrReadOnly]

class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['rating']
    ordering = ['-created_at']

    def get_queryset(self):
        product_pk = self.kwargs['product_pk']
        return ProductReview.objects.filter(product_id=product_pk)

    def perform_create(self, serializer):
        product_pk = self.kwargs['product_pk']
        
        if ProductReview.objects.filter(
            product_id=product_pk, 
            user=self.request.user
        ).exists():
            raise serializers.ValidationError("You have already reviewed this product")
        
        serializer.save(
            user=self.request.user,
            product_id=product_pk
        )

# -------------------
# ORDER
# -------------------
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        """Create order from cart items"""
        # Check if user wants to create from cart
        from_cart = request.data.get('from_cart', False)
        
        if from_cart:
            return self.create_order_from_cart(request)
        else:
            # Use the normal order creation with explicit items
            return super().create(request, *args, **kwargs)
    
    def create_order_from_cart(self, request):
        """Create an order from the user's cart items"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            
            if not cart_items.exists():
                return Response(
                    {'error': 'Cart is empty'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare order data
            order_data = {
                'shipping_address': request.data.get('shipping_address'),
                'phone': request.data.get('phone'),
                'items': []
            }
            
            # Convert cart items to order items
            for cart_item in cart_items:
                if cart_item.quantity is None or cart_item.quantity <= 0:
                    continue
                    
                if cart_item.variant.price is None:
                    return Response(
                        {'error': f'Price not set for {cart_item.variant.product.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                order_data['items'].append({
                    'variant_id': str(cart_item.variant.id),
                    'quantity': cart_item.quantity
                })
            
            # Validate and create order
            serializer = self.get_serializer(data=order_data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save(user=request.user)
            
            # Clear the cart after successful order creation
            cart.items.all().delete()
            
            return Response(
                OrderSerializer(order, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
            
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

# -------------------
# CART
# -------------------
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request):
        """Get user's cart, create if doesn't exist"""
        try:
            # Try to get existing cart
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            # Create new cart if it doesn't exist
            try:
                cart = Cart.objects.create(user=request.user)
            except IntegrityError:
                # Handle race condition - cart was created by another request
                cart = Cart.objects.get(user=request.user)
        
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart with proper error handling"""
        # Get or create cart with proper error handling
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            try:
                cart = Cart.objects.create(user=request.user)
            except IntegrityError:
                # Cart was created by another request between check and create
                cart = Cart.objects.get(user=request.user)
        
        serializer = CartItemCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            variant_id = serializer.validated_data['variant_id']
            quantity = serializer.validated_data['quantity']
            
            try:
                # Check if variant exists and is in stock
                variant = ProductVariant.objects.get(id=variant_id)
                if variant.inventory_quantity <= 0:
                    return Response(
                        {'error': 'Product variant is out of stock'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check if item already exists in cart
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    variant=variant,
                    defaults={'quantity': quantity}
                )
                
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
                
                return Response(
                    {'message': 'Item added to cart', 'cart_item_id': str(cart_item.id)},
                    status=status.HTTP_201_CREATED
                )
                
            except ProductVariant.DoesNotExist:
                return Response(
                    {'error': 'Product variant does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear user's cart"""
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'})


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

# -------------------
# WISHLIST
# -------------------
class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        if self.action == 'create':
            return WishlistCreateSerializer
        return WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product_id = serializer.validated_data['product_id']
        
        # Check if already in wishlist
        if Wishlist.objects.filter(
            user=self.request.user, 
            product_id=product_id
        ).exists():
            raise serializers.ValidationError("Product already in wishlist")
        
        serializer.save(user=self.request.user, product_id=product_id)
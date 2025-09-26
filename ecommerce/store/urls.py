from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from django.urls import path, include
from .views import (
    UserViewSet, CategoryViewSet, ProductViewSet, ProductImageViewSet,
    ProductReviewViewSet, OrderViewSet, OrderItemViewSet,
    WishlistViewSet, PaymentViewSet, CartViewSet, CartItemViewSet
)

# Base router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')

# Nested router for product reviews and images
products_router = routers.NestedDefaultRouter(router, r'products', lookup='product')
products_router.register(r'reviews', ProductReviewViewSet, basename='product-reviews')
products_router.register(r'images', ProductImageViewSet, basename='product-images')

# Nested router for order items
orders_router = routers.NestedDefaultRouter(router, r'orders', lookup='order')
orders_router.register(r'items', OrderItemViewSet, basename='order-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(orders_router.urls)),
]
# store/urls.py
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from django.urls import path, include
from .views import (
    UserViewSet, CategoryViewSet, ProductViewSet, ProductImageViewSet,
    ProductReviewViewSet, OrderViewSet, OrderItemViewSet,
    WishlistViewSet, PaymentViewSet, CartViewSet, CartItemViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-images', ProductImageViewSet, basename='productimage')
# router.register(r'product-reviews', ProductReviewViewSet, basename='productreview')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')

# Nested router for product reviews
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', ProductReviewViewSet, basename='product-reviews')

# Nested router for product images (optional)
# products_router.register('images', views.ProductImageViewSet, basename='product-images')


urlpatterns = [
    path('', include(router.urls)),
]

from django.contrib import admin

# Register your models here.
from .models import (
    CustomUser, Category, Product, ProductImage, ProductReview,
    Order, OrderItem, Wishlist, Payment, Cart, CartItem
)


# -------------------
# CUSTOM USER
# -------------------
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_verified", "is_staff", "created_at")
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = ("is_verified", "is_staff", "is_superuser")
    ordering = ("-created_at",)


# -------------------
# CATEGORY
# -------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)


# -------------------
# PRODUCT
# -------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "status", "inventory_quantity", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


# -------------------
# PRODUCT IMAGE
# -------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_main", "sort_order", "created_at")
    list_filter = ("is_main",)
    search_fields = ("product__name",)


# -------------------
# PRODUCT REVIEW
# -------------------
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "user__email")


# -------------------
# ORDER
# -------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "id")
    inlines = [OrderItemInline]


# -------------------
# ORDER ITEM
# -------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")
    search_fields = ("order__id", "product__name")


# -------------------
# WISHLIST
# -------------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__email", "product__name")


# -------------------
# PAYMENT
# -------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "status", "amount", "created_at")
    list_filter = ("status", "method", "created_at")
    search_fields = ("order__id", "transaction_id")


# -------------------
# CART
# -------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__email",)
    inlines = [CartItemInline]


# -------------------
# CART ITEM
# -------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "created_at")
    search_fields = ("cart__user__email", "product__name")
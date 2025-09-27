from decimal import Decimal
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Category, Product, ProductVariant, ProductImage, 
    ProductReview, Order, OrderItem, Wishlist, Payment, Cart, CartItem
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_verified', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'is_verified')
        }),
    )

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'price', 'compare_at_price', 'inventory_quantity', 'low_stock_threshold')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main', 'sort_order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'is_in_stock', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductImageInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'category', 'status')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'price', 'inventory_quantity', 'is_in_stock')
    list_filter = ('size', 'product__category')
    search_fields = ('product__name',)
    list_editable = ('price', 'inventory_quantity')  # Allow quick editing
    
    def save_model(self, request, obj, form, change):
        # Ensure price is set
        if obj.price is None:
            obj.price = Decimal('0.00')
        super().save_model(request, obj, form, change)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'is_main', 'sort_order')
    list_filter = ('is_main', 'product')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__email')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('display_total_price',)  # Use custom method instead of property
    fields = ('variant', 'quantity', 'price', 'display_total_price')
    
    def display_total_price(self, obj):
        """Safe display of total price for admin"""
        if obj.pk:  # Only if object is saved
            return f"${obj.total_price:.2f}"
        return "N/A"  # For unsaved objects
    display_total_price.short_description = 'Total Price'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'display_total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'id')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')
    
    def display_total_amount(self, obj):
        """Safe display of total amount"""
        if obj.total_amount is None:
            return "N/A"
        return f"${obj.total_amount:.2f}"
    display_total_amount.short_description = 'Total Amount'
    
    def save_model(self, request, obj, form, change):
        """Ensure order has valid total amount"""
        if obj.total_amount is None:
            # Calculate total from items if not set
            total = Decimal('0.00')
            for item in obj.items.all():
                if item.total_price is not None:
                    total += item.total_price
            obj.total_amount = total
        super().save_model(request, obj, form, change)
    
    def save_related(self, request, form, formsets, change):
        """Save order items and recalculate total"""
        super().save_related(request, form, formsets, change)
        
        # Recalculate total amount after saving items
        order = form.instance
        total = Decimal('0.00')
        for item in order.items.all():
            if item.quantity is not None and item.price is not None:
                total += item.quantity * item.price
        
        if total != order.total_amount:
            order.total_amount = total
            order.save(update_fields=['total_amount'])



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'status', 'amount', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('order__id', 'transaction_id')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_amount', 'created_at')
    search_fields = ('user__email',)
    inlines = [CartItemInline]

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'product__name')
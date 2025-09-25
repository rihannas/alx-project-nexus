# store/serializers.py
from django.db import models
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import (
    CustomUser, Category, Product, ProductImage, ProductReview,
    Order, OrderItem, Wishlist, Payment, Cart, CartItem
)


# -------------------
# USER
# -------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "phone_number", "is_verified", "created_at", "updated_at"
        ]

class CustomRegisterSerializer(RegisterSerializer):
    """Custom registration serializer"""
    first_name = serializers.CharField(required=False, max_length=30)
    last_name = serializers.CharField(required=False, max_length=30)
    phone = serializers.CharField(required=False, max_length=15)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone': self.validated_data.get('phone', ''),
        })
        return data

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone = self.cleaned_data.get('phone')
        user.save()
        return user



# -------------------
# CATEGORY
# -------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# -------------------
# PRODUCT + IMAGES + REVIEWS
# -------------------

class ReviewUserSerializer(serializers.Serializer):
    """Only expose the username of the review user"""
    username = serializers.CharField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_main", "sort_order"]



class ProductReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ["id", "user", "rating", "title", "comment", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "category",
            "price", "compare_at_price", "track_inventory", "inventory_quantity",
            "low_stock_threshold", "size", "status",
            "meta_title", "meta_description",
            "is_on_sale", "discount_percentage",
            "is_in_stock", "is_low_stock",
            "images"
        ]
        

# store/serializers.py
class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "id", "size", "price", "compare_at_price",
            "inventory_quantity", "low_stock_threshold",
            "is_on_sale", "discount_percentage",
            "is_in_stock", "is_low_stock"
        ]
        read_only_fields = ["is_on_sale", "discount_percentage", "is_in_stock", "is_low_stock"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "category",
            "status", "meta_title", "meta_description",
            "is_in_stock", "images", "variants"
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = ProductReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_name',
            'status', 'is_in_stock', 'images',
            'variants', 'review_count', 'average_rating', 'reviews'
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        return round(avg, 1) if avg else 0


# -------------------
# ORDER + ITEMS + PAYMENT
# -------------------
class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "variant", "quantity", "price", "total_price"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user", "status", "total_amount",
            "shipping_address", "phone",
            "created_at", "updated_at", "items", "payment"
        ]


# -------------------
# WISHLIST
# -------------------
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "user", "product", "created_at"]


# -------------------
# CART + CART ITEMS
# -------------------
class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "variant", "quantity", "total_price"]



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_amount", "total_items"]

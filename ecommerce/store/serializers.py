from django.db import models
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import (
    CustomUser, Category, Product, ProductImage, ProductReview,
    Order, OrderItem, Wishlist, Payment, Cart, CartItem, ProductVariant
)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extend JWT token serializer to include extra user data in the response
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom fields to the response body (not just token payload)
        data.update({
            'email': self.user.email,
            'username': self.user.username,
        })
        return data
    

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

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    phone_number = serializers.CharField(required=False, allow_blank=True)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', ''),
            'password': self.validated_data.get('password', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
        }

# -------------------
# CATEGORY
# -------------------
class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "image", "product_count", "created_at"]
        
    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()

# -------------------
# PRODUCT VARIANTS
# -------------------
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

# -------------------
# PRODUCT IMAGES
# -------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_main", "sort_order"]

# -------------------
# PRODUCT REVIEWS
# -------------------
class ReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name"]

class ProductReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = ["id", "user", "rating", "title", "comment", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]

# -------------------
# PRODUCTS
# -------------------
class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists"""
    category = CategorySerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    available_sizes = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "category",
            "status", "is_in_stock", "main_image", 
            "price_range", "available_sizes", "created_at"
        ]
    
    def get_main_image(self, obj):
        main_image = obj.main_image
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None
    
    def get_price_range(self, obj):
        variants = obj.variants.filter(inventory_quantity__gt=0)
        if not variants.exists():
            return None
        
        prices = variants.values_list('price', flat=True)
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return {"min": float(min_price), "max": float(max_price)}
        return {"min": float(min_price), "max": float(max_price)}
    
    def get_available_sizes(self, obj):
        return list(obj.variants.filter(
            inventory_quantity__gt=0
        ).values_list('size', flat=True).distinct())

class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view"""
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'status', 'meta_title', 'meta_description',
            'is_in_stock', 'images', 'variants', 
            'reviews', 'review_count', 'average_rating',
            'created_at', 'updated_at'
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        return round(avg, 1) if avg else 0

# -------------------
# CART
# -------------------
class CartItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cart items"""
    variant_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['variant_id', 'quantity']
    
    def validate_variant_id(self, value):
        try:
            variant = ProductVariant.objects.get(id=value)
            if variant.inventory_quantity <= 0:
                raise serializers.ValidationError("Product variant is out of stock")
            return value
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("Product variant does not exist")

class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "variant", "product_name", "product_image", "quantity", "total_price", "created_at"]
    
    def get_product_image(self, obj):
        main_image = obj.variant.product.main_image
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_amount", "total_items", "created_at"]

# -------------------
# ORDER
# -------------------
class OrderItemCreateSerializer(serializers.ModelSerializer):
    variant_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['variant_id', 'quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "variant", "product_name", "quantity", "price", "total_price"]

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone', 'items']
    
    def validate(self, data):
        """Validate order data before creation"""
        items_data = data.get('items', [])
        if not items_data:
            raise serializers.ValidationError("Order must contain at least one item")
        return data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Calculate total amount
        total_amount = Decimal('0.00')
        order_items = []
        
        for item_data in items_data:
            try:
                variant = ProductVariant.objects.get(id=item_data['variant_id'])
                quantity = item_data['quantity']
                
                # Validate data
                if quantity is None or quantity <= 0:
                    raise serializers.ValidationError(f"Invalid quantity for {variant.product.name}")
                
                if variant.price is None:
                    raise serializers.ValidationError(f"Price not set for {variant.product.name}")
                
                # Check stock
                if variant.inventory_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {variant.product.name} - {variant.size}. "
                        f"Available: {variant.inventory_quantity}, Requested: {quantity}"
                    )
                
                item_total = variant.price * quantity
                total_amount += item_total
                
                order_items.append({
                    'variant': variant,
                    'quantity': quantity,
                    'price': variant.price  # Ensure price is set
                })
                
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError(f"Product variant {item_data['variant_id']} does not exist")
        
        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            **validated_data
        )
        
        # Create order items and update inventory
        for item_data in order_items:
            OrderItem.objects.create(
                order=order,
                variant=item_data['variant'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            
            # Update inventory
            variant = item_data['variant']
            variant.inventory_quantity -= item_data['quantity']
            variant.save()
        
        return order

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user", "status", "total_amount",
            "shipping_address", "phone", "items",
            "created_at", "updated_at"
        ]
        read_only_fields = ['user', 'total_amount']

# -------------------
# PAYMENT
# -------------------
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ['created_at']

# -------------------
# WISHLIST
# -------------------
class WishlistCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['product_id']

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "created_at"]

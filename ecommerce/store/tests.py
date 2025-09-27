from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from .models import Category, Product, ProductVariant, Cart, CartItem, Order

User = get_user_model()

class ProductTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            category=self.category,
            status='active'
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            price=Decimal('29.99'),
            inventory_quantity=100
        )

    def test_product_list(self):
        """Test product list endpoint"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_detail(self):
        """Test product detail endpoint"""
        response = self.client.get(f'/api/products/{self.product.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_product_filtering(self):
        """Test product filtering by category"""
        response = self.client.get(f'/api/products/?category={self.category.slug}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class CartTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            status='active'
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            price=Decimal('29.99'),
            inventory_quantity=100
        )

    def test_add_to_cart(self):
        """Test adding item to cart"""
        data = {
            'variant_id': str(self.variant.id),
            'quantity': 2
        }
        response = self.client.post('/api/carts/add_item/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_cart(self):
        """Test getting user's cart"""
        # Add item to cart first
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=1
        )
        
        response = self.client.get('/api/carts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)


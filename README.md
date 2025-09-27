# ALX Project Nexus 🚀

Welcome to **alx-project-nexus** — my documentation hub for everything I’ve learned during the **ProDev Backend Engineering Program**.  
This repo is a reflection of my growth as a backend engineer, highlighting key technologies, concepts, challenges, and personal takeaways that shaped my journey.

---

## 📚 Program Overview

The **ProDev Backend Engineering Program** is designed to provide practical, real-world experience in building scalable and reliable backend systems.  
It covered a wide range of tools, frameworks, and concepts — from foundational backend principles to advanced production-level practices.

---

## 🔑 Major Learnings

### 🛠 Key Technologies

- **Python** – clean, efficient programming for backend services
- **Django** – building robust, scalable applications
- **Django REST Framework (DRF)** – creating and managing REST APIs
- **GraphQL** – flexible and efficient data querying
- **Docker** – containerization for consistent environments
- **CI/CD** – automating deployment pipelines for reliability

### 💡 Backend Development Concepts

- **Database Design** – normalization, relationships, and schema optimization
- **Asynchronous Programming** – handling concurrent tasks efficiently
- **Caching Strategies** – improving performance and scalability
- **Authentication & Authorization** – securing APIs and services
- **Error Handling & Logging** – maintaining system reliability

---

## ⚡ Challenges & Solutions

- **Challenge:** Debugging complex API responses  
  **Solution:** Learned to use Postman, logging, and DRF serializers effectively

- **Challenge:** Deploying apps across different environments  
  **Solution:** Adopted **Docker** for consistency and smoother deployments

- **Challenge:** Managing async tasks and background jobs  
  **Solution:** Explored **Celery** and async programming patterns

---

## 📊 Database Models

### User Management

- **CustomUser**: Extended user model with email authentication
- **Fields**: email, phone_number, is_verified, timestamps
- **Authentication**: JWT-based with email as username

### Product Catalog

- **Category**: Hierarchical product categories with images
- **Product**: Main product information with status management
- **ProductVariant**: Size-specific pricing and inventory (XS-XXL)
- **ProductImage**: Multiple images per product with main image support
- **ProductReview**: User reviews and ratings (1-5 stars)

### Order Management

- **Order**: Customer orders with status tracking
- **OrderItem**: Individual order items with price snapshots
- **Payment**: Payment processing with multiple methods

### Shopping Features

- **Cart**: User shopping cart with persistent storage
- **CartItem**: Cart items with quantity management
- **Wishlist**: User wishlist functionality

## 🔌 API Endpoints

### Authentication & Users

| Method | Endpoint                  | Description              | Authentication |
| ------ | ------------------------- | ------------------------ | -------------- |
| POST   | `/api/auth/registration/` | User registration        | Public         |
| POST   | `/api/auth/jwt/create/`   | JWT login                | Public         |
| POST   | `/api/auth/jwt/refresh/`  | Refresh JWT token        | Public         |
| POST   | `/api/auth/jwt/verify/`   | Verify JWT token         | Public         |
| GET    | `/api/auth/user/`         | Get user details         | JWT Required   |
| GET    | `/api/store/users/me/`    | Get current user profile | JWT Required   |

### Categories

| Method    | Endpoint                        | Description          | Authentication |
| --------- | ------------------------------- | -------------------- | -------------- |
| GET       | `/api/store/categories/`        | List all categories  | Public         |
| POST      | `/api/store/categories/`        | Create category      | Admin Only     |
| GET       | `/api/store/categories/{slug}/` | Get category details | Public         |
| PUT/PATCH | `/api/store/categories/{slug}/` | Update category      | Admin Only     |
| DELETE    | `/api/store/categories/{slug}/` | Delete category      | Admin Only     |

### Products

| Method    | Endpoint                                    | Description                | Authentication |
| --------- | ------------------------------------------- | -------------------------- | -------------- |
| GET       | `/api/store/products/`                      | List products (filterable) | Public         |
| POST      | `/api/store/products/`                      | Create product             | Admin Only     |
| GET       | `/api/store/products/{slug}/`               | Get product details        | Public         |
| PUT/PATCH | `/api/store/products/{slug}/`               | Update product             | Admin Only     |
| DELETE    | `/api/store/products/{slug}/`               | Delete product             | Admin Only     |
| GET       | `/api/store/products/{slug}/variants/`      | Get product variants       | Public         |
| GET       | `/api/store/products/{product_pk}/reviews/` | Get product reviews        | Public         |
| POST      | `/api/store/products/{product_pk}/reviews/` | Create review              | JWT Required   |

### Shopping Cart

| Method    | Endpoint                      | Description      | Authentication |
| --------- | ----------------------------- | ---------------- | -------------- |
| GET       | `/api/store/carts/`           | Get user cart    | JWT Required   |
| POST      | `/api/store/carts/add_item/`  | Add item to cart | JWT Required   |
| POST      | `/api/store/carts/clear/`     | Clear cart       | JWT Required   |
| GET       | `/api/store/cart-items/`      | List cart items  | JWT Required   |
| POST      | `/api/store/cart-items/`      | Add cart item    | JWT Required   |
| PUT/PATCH | `/api/store/cart-items/{id}/` | Update cart item | JWT Required   |
| DELETE    | `/api/store/cart-items/{id}/` | Remove cart item | JWT Required   |

### Orders & Payments

| Method | Endpoint                              | Description       | Authentication |
| ------ | ------------------------------------- | ----------------- | -------------- |
| GET    | `/api/store/orders/`                  | List user orders  | JWT Required   |
| POST   | `/api/store/orders/`                  | Create order      | JWT Required   |
| GET    | `/api/store/orders/{id}/`             | Get order details | JWT Required   |
| GET    | `/api/store/orders/{order_pk}/items/` | Get order items   | JWT Required   |
| GET    | `/api/store/payments/`                | List payments     | JWT Required   |
| POST   | `/api/store/payments/`                | Create payment    | JWT Required   |

### Wishlist

| Method | Endpoint                     | Description          | Authentication |
| ------ | ---------------------------- | -------------------- | -------------- |
| GET    | `/api/store/wishlists/`      | Get user wishlist    | JWT Required   |
| POST   | `/api/store/wishlists/`      | Add to wishlist      | JWT Required   |
| DELETE | `/api/store/wishlists/{id}/` | Remove from wishlist | JWT Required   |

## 🔍 Features & Functionality

### Product Management

- **Status-based filtering**: Draft, Active, Inactive, Discontinued
- **Variant system**: Size-specific pricing and inventory
- **Image management**: Multiple images with main image support
- **SEO optimization**: Meta titles and descriptions
- **Review system**: User ratings and comments

### Shopping Experience

- **Advanced filtering**: Price, category, size, rating
- **Search functionality**: Product name and description
- **Sorting options**: Price, date, name
- **Stock management**: Low stock alerts, inventory tracking
- **Wishlist**: Save products for later

### Order Processing

- **Multi-step workflow**: Pending → Processing → Shipped → Delivered
- **Inventory deduction**: Automatic stock updates on order creation
- **Price snapshotting**: Order items preserve original prices
- **Cart conversion**: Convert cart to order with single API call

### User Features

- **JWT authentication**: Secure token-based auth
- **Profile management**: Personal information and preferences
- **Order history**: Complete purchase history
- **Review management**: Product reviews and ratings

## ⚙️ Configuration

### Django Settings Key Features:

- **JWT Authentication**: 30-minute access tokens, 7-day refresh tokens
- **CORS Enabled**: Cross-origin requests allowed
- **Pagination**: 12 items per page (configurable)
- **Media Handling**: Image uploads to `/media/` directory
- **API Documentation**: Swagger & ReDoc at `/swagger/` and `/redoc/`

### Database Configuration:

- **PostgreSQL**: Primary database for all data
- **Redis**: Session storage and cache
- **RabbitMQ**: Message queue for async tasks

## 🛠️ Development

### Running Tests

```bash
docker-compose run web python manage.py test
```

### Database Migrations

```bash
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate
```

### Admin Access

Create superuser:

```bash
docker-compose run web python manage.py createsuperuser
```

### Environment Variables

Key environment variables for configuration:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated hostnames
- Database credentials (POSTGRES\_\*)
- JWT configuration options

## 🔒 Security Features

- **JWT Authentication**: Secure token-based access
- **Password Validation**: Django's built-in password validators
- **CORS Configuration**: Controlled cross-origin requests
- **Input Validation**: Comprehensive serializer validation
- **Permission System**: Role-based access control
- **SQL Injection Protection**: Django ORM usage

## 📈 Performance Optimizations

- **Database Indexing**: Optimized queries on frequently accessed fields
- **Query Optimization**: Prefetch related objects to avoid N+1 queries
- **Pagination**: Controlled data retrieval for large datasets
- **Caching**: Redis integration for frequently accessed data
- **Async Tasks**: Celery for background processing

✨ This repository will continue to evolve as I do. Backend engineering is a journey — and this is just the beginning!

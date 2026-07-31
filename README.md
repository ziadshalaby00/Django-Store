# Django Store

A full-featured e-commerce REST API built with Django. Supports product cataloging, shopping cart, order management, Paymob payments, JWT authentication with cookies, and Google OAuth.

## 🛠️ Tech Stack

- **Backend:** Django 5.2, Django REST Framework
- **Database:** PostgreSQL
- **Cache / Tasks:** Redis, Celery, django-celery-beat
- **Authentication:** JWT (SimpleJWT), Google OAuth2, CSRF Protection
- **Payments:** Paymob
- **Media Processing:** Pillow
- **Environment Management:** django-environ

## ✨ Features

### 🔐 Authentication
- User registration and login
- JWT authentication with **httpOnly cookies**
- Google OAuth2 login
- Password reset
- Profile update and account deletion

### 🛍️ Products
- Product categories and brands
- Filtering, searching, and pagination
- Multi-image support
- Product reviews and ratings

### 🛒 Shopping Cart
- Add, update, and remove cart items
- Stock validation
- Maximum quantity limits

### 📦 Orders
- Create orders directly from the shopping cart
- Snapshot shipping address at checkout
- Unpaid order limits
- Exponential cooling period for expired orders
- Automatic stock restoration after order expiration

### 💳 Payments
- Paymob payment gateway integration
- Webhook callback handling
- Payment link expiration support

### 📍 Addresses
- Multiple labeled addresses per user

### ⚙️ Admin Dashboard
- Custom admin dashboard
- Collapsible filters
- User statistics

from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
from product.models import Product
from address.models import Address

User = get_user_model()


class Order(models.Model):
    PAID_STATUS = [
        ('pending', 'Pending'),
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]

    PAYMENT_METHODS = [
        ("cod", "Cash on Delivery"),
        ("card", "EasyCash / Online Card"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="card")
    
    payment_status = models.CharField(max_length=20, choices=PAID_STATUS, default="unpaid")
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)  # تاريخ الدفع لو اتدفع

    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name="shipping_orders"
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default="EGP", editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.payment_status}"

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save()
        return self.total_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.quantity} × {self.product.name if self.product else 'Deleted product'}"

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity

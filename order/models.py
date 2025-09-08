from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.
from django.contrib.auth import get_user_model
from product.models import Product
from address.models import Address
from django.conf import settings
import uuid

User = get_user_model()


class Order(models.Model):
    PAID_STATUS = [
        ('pending', 'Pending'),
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("unpayable", "Unpayable"),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="orders")
    payment_method = models.CharField(
        max_length=20,
        choices=getattr(settings, "AVAILABLE_PAYMENT_METHODS", [
            ("cod", "Cash on Delivery"),
            ("paymob", "Paymob Online Payment"),
        ]),
        default="paymob"
    )
    
    payment_status = models.CharField(max_length=20, choices=PAID_STATUS, default="unpaid")
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)  # تاريخ الدفع لو اتدفع

    shipping_address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="shipping_orders"
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default="EGP", editable=False)
    
    # --- New field ---
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            # توليد رقم أوردر بصيغة منظمة
            # مثال: ORD-20250908-AB12CD
            import datetime
            today = datetime.date.today().strftime("%Y%m%d")
            random_code = uuid.uuid4().hex[:6].upper()
            self.order_number = f"ORD-{today}-{random_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        username = self.user.username if self.user else "Deleted user"
        return f"Order {self.order_number} - {username} - {self.payment_status}"

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save()
        return self.total_price

    def set_status(self, new_status: str):
        """
        Update order status + handle stock if expired
        """
        # لو الأوردر بقى expired → رجع المخزون
        if new_status == "expired" and self.payment_status != "expired":
            for item in self.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()

        # لو الأوردر اتدفع → علمه paid وخزن تاريخ الدفع
        if new_status == "paid":
            self.is_paid = True
            from django.utils import timezone
            self.paid_at = timezone.now()

        self.payment_status = new_status
        self.save()


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
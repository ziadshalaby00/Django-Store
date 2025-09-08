from django.db import models

# Create your models here.
from order.models import Order


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),    # تم إنشاؤه لكن لسه الدفع ماحصلش
        ("success", "Success"),    # اتدفع بنجاح
        ("failed", "Failed"),      # فشل
    ]

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="EGP", editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    is_paid = models.BooleanField(default=False)  # لو الدفع تم بنجاح

    # محاولات الدفع أحيانًا بيكون ليها "session" أو "intent id" من بوابة الدفع
    provider = models.CharField(max_length=50, blank=True, null=True)   # Stripe, Paymob, Fawry...
    provider_payment_id = models.CharField(max_length=100, blank=True, null=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order.id} - {self.status}"

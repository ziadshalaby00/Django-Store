from django.db import models
from django.contrib.auth import get_user_model
from order.models import Order  # Assuming you have an Order model

User = get_user_model()

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),   
        ("success", "Success"),  
        ("failed", "Failed"),  
        ("canceled", "Canceled"),  
    ]

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="payments", on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="EGP", editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_paid = models.BooleanField(default=False)

    provider = models.CharField(max_length=50, blank=True, null=True)   # Paymob, Stripe, Fawry
    provider_payment_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    payment_method = models.CharField(max_length=255, blank=True, null=True)  # e.g., credit_card, wallet, etc.

    paymob_order_id = models.CharField(max_length=255, unique=True) 

    client_secret = models.CharField(max_length=255, blank=True, null=True)  
    payment_url = models.URLField(blank=True, null=True)

    # Webhook
    webhook_payload = models.JSONField(blank=True, null=True) 
    webhook_received = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order.id} - {self.status}"

    def mark_as_paid(self):
        """Helper method to mark payment as paid"""
        self.status = "success"
        self.is_paid = True
        self.save()

    def mark_as_failed(self):
        """Helper method to mark payment as failed"""
        self.status = "failed"
        self.is_paid = False
        self.save()
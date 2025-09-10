from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model

User = get_user_model()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="addresses")
    label = models.CharField(max_length=100)
    
    full_name = models.CharField(max_length=100)  # اسم صاحب العنوان
    phone = models.CharField(max_length=20)

    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default="Egypt")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "label"], name="unique_user_address_label")
        ]

    def __str__(self):
        return f"{self.full_name} - {self.street}, {self.city}, {self.country}"

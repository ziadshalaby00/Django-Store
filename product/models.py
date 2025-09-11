from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # السعر الأصلي
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # الخصم %
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name[:50]

    @property
    def price_after_discount(self):
        """السعر بعد تطبيق الخصم النسبي"""
        if self.price is None:
            return None
        if self.discount_percentage is None:
            discount = 0
        else:
            discount = self.discount_percentage
        return round(self.price * (1 - discount / 100), 2)

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sub_images"
    )
    image = models.ImageField(upload_to="products/sub_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sub Image for {self.product.name}"


from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Product)
def update_is_active_based_on_stock(sender, instance, **kwargs):
    """
    هذا السينيال يتأكد أن is_active متوافقة مع stock.
    - stock > 0 → is_active = True
    - stock = 0 → is_active = False
    """
    instance.is_active = instance.stock > 0
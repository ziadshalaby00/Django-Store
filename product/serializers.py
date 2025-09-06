from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    price_before_discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_after_discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price_before_discount',
            'price_after_discount',
            'discount_percentage',
            'stock',
            'image',
            'brand',
            'category',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

from rest_framework import serializers
from .models import Category, Brand

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

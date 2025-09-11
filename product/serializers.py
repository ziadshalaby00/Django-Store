from rest_framework import serializers
from .models import Product
from reviews.serializers import ReviewSerializer

class ProductSerializer(serializers.ModelSerializer):
    price_after_discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'price_after_discount',
            'discount_percentage',
            'stock',
            'image',
            'brand',
            'category',
            'is_active',
            "average_rating",
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0

from .models import ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ProductDetailSerializer(ProductSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    sub_images = ProductImageSerializer(many=True, read_only=True)  # 👈 أضفنا الصور الإضافية
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['reviews', 'sub_images']


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

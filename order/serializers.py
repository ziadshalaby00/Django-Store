from rest_framework import serializers
from .models import Order, OrderItem, OrderAddress

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ("id", "product", "p_name", 'p_description', 'p_image', "quantity", "price_at_purchase", "subtotal")

    def get_subtotal(self, obj):
        # subtotal مع العملة
        return f"{obj.subtotal} {obj.order.currency}"

class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = [
            "id",
            "label",
            "full_name",
            "phone",
            "street",
            "city",
            "state",
            "postal_code",
            "country",
            "created_at",
        ]
        read_only_fields = ["order", "id", "created_at"]
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = OrderAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "user",
            "total_price",
            "currency",
            "payment_status",
            "is_paid",
            "paid_at",
            "payment_method",
            "shipping_address",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "order_number", "user", "total_price", "currency", "payment_status", "is_paid", "paid_at", "items", "created_at", "updated_at",)

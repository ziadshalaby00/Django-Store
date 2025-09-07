from rest_framework import serializers
from .models import Order, OrderItem
from address.serializers import AddressSerializer  # لو عندك Serializer للعناوين

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "price_at_purchase", "subtotal")

    def get_subtotal(self, obj):
        # subtotal مع العملة
        return f"{obj.subtotal} {obj.order.currency}"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
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
        read_only_fields = ("total_price", "currency", "items", "created_at", "updated_at")

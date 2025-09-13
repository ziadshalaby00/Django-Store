from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from cart.models import Cart, CartItem
from .models import Order, OrderItem, OrderAddress
from .serializers import OrderSerializer
from address.models import Address
from django.db import transaction

from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.conf import settings
from product.models import Product

class CreateOrderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        # تأكد من وجود عنوان شحن
        try:
            shipping_address = request.data.get("shipping_address_id")
            shipping_address = Address.objects.get(id=shipping_address, user=user)
        except Address.DoesNotExist:
            return Response(
                {"detail": "You must have a shipping address to place an order."},
                status=status.HTTP_400_BAD_REQUEST
            )

        unpaid_orders_count = Order.objects.filter(user=request.user, is_paid=False).exclude(payment_status="expired").count()
        if unpaid_orders_count >= settings.MAX_UNPAID_ORDERS_PER_USER:
            return Response({
                "detail": f"You have reached the maximum of {settings.MAX_UNPAID_ORDERS_PER_USER} unpaid orders. please pay for existing orders before creating new ones. or wait for them to expire."
            }, status=status.HTTP_400_BAD_REQUEST)

        # جلب الكارت ومحتوياته
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.items.select_related('product').all()
        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Lock the products in the cart
                product_ids = [item.product_id for item in cart_items]
                products = Product.objects.select_for_update().filter(id__in=product_ids)
                product_map = {p.id: p for p in products}

                method_key = request.data.get('payment_method', '').upper()
                if method_key not in [k[0] for k in settings.AVAILABLE_PAYMENT_METHODS]:
                    return Response({"detail": "Invalid payment method."}, status=status.HTTP_400_BAD_REQUEST)
                
                order = Order.objects.create(
                    user=user,
                    payment_method=method_key
                )
                
                OrderAddress.objects.create(
                    order=order,
                    label=shipping_address.label,
                    full_name=shipping_address.full_name,
                    phone=shipping_address.phone,
                    street=shipping_address.street,
                    city=shipping_address.city,
                    state=shipping_address.state,
                    postal_code=shipping_address.postal_code,
                    country=shipping_address.country,
                )

                order_items = []
                for item in cart_items:
                    product = product_map[item.product_id]

                    if item.quantity > settings.MAX_QTY_PER_ITEM:
                        raise ValidationError(
                            f"The maximum quantity per product is {settings.MAX_QTY_PER_ITEM}."
                        )

                    if product.stock < item.quantity:
                        raise ValidationError(
                            {"detail": f"Only {product.stock} items available in stock for product {product.name}."}
                        )

                    if item.quantity < 1:
                        raise ValidationError("Invalid quantity.")

                    product.stock -= item.quantity
                    product.save()

                    order_items.append(OrderItem(
                        order=order,
                        product=product,
                        p_name=product.name,
                        p_description=product.description,
                        p_image=product.image,
                        quantity=item.quantity,
                        price_at_purchase=product.price_after_discount
                    ))

                OrderItem.objects.bulk_create(order_items)
                order.calculate_total()
                cart_items.delete()

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

class UserOrdersAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # جلب جميع الأوردرات الخاصة بالمستخدم، ترتيب من الأحدث
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PaymentMethodsAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # لو عايز أي حد يشوفها

    def get(self, request):
        # إرجاع قائمة الـ choices
        methods = getattr(settings, "AVAILABLE_PAYMENT_METHODS", [
            ("COD", "Cash on Delivery"),
            ("EPAY", "E-payment"),
        ])
        return Response([
            {"value": key, "display": label} for key, label in methods
        ], status=status.HTTP_200_OK)
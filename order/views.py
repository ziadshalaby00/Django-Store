from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer
from address.models import Address
from django.db import transaction

from django.db import transaction
from rest_framework.exceptions import ValidationError

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

        # جلب الكارت ومحتوياته
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                order = Order.objects.create(
                    user=user,
                    shipping_address=shipping_address,
                    payment_method=request.data.get("payment_method", "card")
                )

                order_items = []
                for item in cart_items:
                    product = item.product
                    if product.stock < item.quantity:
                        # لو الكمية مش كافية، ارفع Exception عشان rollback يحصل
                        raise ValidationError(
                            {"detail": f"Only {product.stock} items available in stock for product {product.name}."}
                        )
                     
                    product.stock -= item.quantity
                    product.save()

                    order_item = OrderItem(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price_at_purchase=product.price
                    )
                    order_items.append(order_item)

                OrderItem.objects.bulk_create(order_items)
                
                # حساب total_price للأوردر
                order.calculate_total()

                # مسح الكارت بعد إنشاء الأوردر
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
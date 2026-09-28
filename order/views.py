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
from django.utils import timezone
from datetime import timedelta

class CreateOrderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def calculate_cooling_period(self, expired_count: int) -> int:
        base = settings.COOLING_PERIOD_AFTER_EXPIRY  # In minutes
        cooling = base * (2 ** (expired_count - 1))  # exponential backoff
        max_cooling = 24 * 60  # 24 hours in minutes
        return min(cooling, max_cooling)  # Returns the value in minutes

    def post(self, request):
        user = request.user

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


        expired_count = Order.objects.filter(
            user=request.user,
            payment_status="expired"
        ).count()

        if expired_count > 0:
            cooling_minutes = self.calculate_cooling_period(expired_count)
            last_expired = Order.objects.filter(
                user=request.user,
                payment_status="expired"
            ).order_by("-updated_at").first()

            cooling_time = last_expired.updated_at + timedelta(minutes=cooling_minutes)
            if timezone.now() < cooling_time:
                remaining_seconds = int((cooling_time - timezone.now()).total_seconds())
                minutes, seconds = divmod(remaining_seconds, 60)

                return Response({
                    "message": (
                        f"Your recent orders have expired. To prevent system abuse, "
                        f"please wait {minutes} minutes and {seconds} seconds before placing a new order."
                    ),
                    "retry_after_seconds": remaining_seconds,
                    "cooling_period_minutes": minutes,
                    "cooling_period_seconds": seconds
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                
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
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PaymentMethodsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        methods = getattr(settings, "AVAILABLE_PAYMENT_METHODS", [
            ("COD", "Cash on Delivery"),
            ("EPAY", "E-payment"),
        ])
        return Response([
            {"value": key, "display": label} for key, label in methods
        ], status=status.HTTP_200_OK)


class BuyNowOrderView(APIView):
    """
    Buy a single product directly without going through the cart.
    POST body:
      - product_id: int
      - quantity: int
      - shipping_address_id: int
      - payment_method: "COD" or "EPAY" (default EPAY)
    """
    permission_classes = [permissions.IsAuthenticated]

    def calculate_cooling_period(self, expired_count: int) -> int:
        base = settings.COOLING_PERIOD_AFTER_EXPIRY
        cooling = base * (2 ** (expired_count - 1))
        return min(cooling, 24 * 60)

    def post(self, request):
        user = request.user

        product_id = request.data.get("product_id")
        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"detail": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

        address_id = request.data.get("shipping_address_id")
        payment_method = str(request.data.get("payment_method", "EPAY")).upper()

        address_id = request.data.get("shipping_address_id")
        shipping_address = None

        if address_id:
            try:
                shipping_address = Address.objects.get(id=address_id, user=user)
            except Address.DoesNotExist:
                shipping_address = None

        if shipping_address is None:
            shipping_address = Address.objects.filter(user=user).first()

        if shipping_address is None:
            shipping_address = Address.objects.create(
                user=user,
                label="Default",
                full_name=user.fullname or user.username,
                phone="01000000000",
                street="Default Street",
                city="Cairo",
                country="Egypt",
            )

        # ---- validate payment method ----
        if payment_method not in [k[0] for k in settings.AVAILABLE_PAYMENT_METHODS]:
            return Response({"detail": "Invalid payment method."}, status=status.HTTP_400_BAD_REQUEST)

        # ---- unpaid orders limit ----
        # unpaid_orders_count = Order.objects.filter(
        #     user=user, is_paid=False
        # ).exclude(payment_status="expired").count()
        # if unpaid_orders_count >= settings.MAX_UNPAID_ORDERS_PER_USER:
        #     return Response(
        #         {"detail": f"You have reached the maximum of {settings.MAX_UNPAID_ORDERS_PER_USER} unpaid orders."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # ---- cooling period after expirations ----
        expired_count = Order.objects.filter(user=user, payment_status="expired").count()
        if expired_count > 0:
            cooling_minutes = self.calculate_cooling_period(expired_count)
            last_expired = Order.objects.filter(
                user=user, payment_status="expired"
            ).order_by("-updated_at").first()
            cooling_time = last_expired.updated_at + timedelta(minutes=cooling_minutes)
            if timezone.now() < cooling_time:
                remaining = int((cooling_time - timezone.now()).total_seconds())
                minutes, seconds = divmod(remaining, 60)
                return Response({
                    "detail": f"Please wait {minutes}m {seconds}s before placing a new order.",
                    "retry_after_seconds": remaining,
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(id=product_id)

                if not product.is_active:
                    return Response({"detail": "Product is not available."}, status=status.HTTP_400_BAD_REQUEST)

                if quantity < 1:
                    return Response({"detail": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

                if quantity > settings.MAX_QTY_PER_ITEM:
                    return Response(
                        {"detail": f"Max quantity per product is {settings.MAX_QTY_PER_ITEM}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if product.stock < quantity:
                    return Response(
                        {"detail": f"Only {product.stock} items available in stock."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                product.stock -= quantity
                product.save()

                order = Order.objects.create(user=user, payment_method=payment_method)

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

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    p_name=product.name,
                    p_description=product.description,
                    p_image=product.image,
                    quantity=quantity,
                    price_at_purchase=product.price_after_discount,
                )

                order.calculate_total()

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
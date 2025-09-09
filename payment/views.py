from django.shortcuts import render

# Create your views here.
# payments/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from order.models import Order
from .models import Payment
import requests
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]  # يمكن تعديلها حسب الحاجة
    """
    Create a payment for an order.
    Handles Paymob (online) or COD (Cash on Delivery).
    """

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # إذا الدفع عند الاستلام
        if order.payment_method.lower() == "cod":
            # تحديث حالة الدفع عند التسليم لاحقًا
            return Response({
                "message": "Order is Cash on Delivery. No payment object created.",
                "order_number": order.order_number,
            }, status=status.HTTP_200_OK)

        # التحقق من حالة الدفع
        if order.payment_status == "paid" or order.is_paid:
            return Response({
                "message": "Order is already paid.",
                "order_number": order.order_number
            }, status=status.HTTP_400_BAD_REQUEST)

        elif order.payment_status == "expired":
            return Response({
                "message": "Payment window expired. You cannot pay this order anymore.",
                "order_number": order.order_number
            }, status=status.HTTP_400_BAD_REQUEST)

        # إذا وصلنا هنا، الدفع ممكن
        payments = order.payments.all().count()
        if payments >= settings.MAX_PAYMENT_ATTEMPTS:
            order.payment_status = "unpayable"
        order.save()
        
        if order.payment_status == "unpayable":
            return Response({
                "message": "Payment attempts exceeded. You cannot pay this order.",
                "order_number": order.order_number
            }, status=status.HTTP_400_BAD_REQUEST)

        # مثال: الدفع عبر Paymob
        if order.payment_method.lower() == "paymob":
            # إعداد بيانات Intention API
            paymob_secret_key = settings.PAYMOB_SECRET_KEY  # ضيف المفتاح في settings.py
            amount = int(order.total_price) * 100  # Paymob expects amount in cents/piasters
            
            payload = {
                "amount": amount,
                "currency": order.currency,
                "payment_methods": settings.PAYMOB_PAYMENT_METHODS,  # أو Integration ID
                "items": [
                    {
                        "name": item.product.name[:50],
                        "amount": int(item.price_at_purchase) * 100,
                        "description": item.product.description[:255] if item.product.description else item.product.name[:255],
                        "quantity": item.quantity
                    } for item in order.items.all()
                ],
                "billing_data": {
                    "first_name": order.shipping_address.full_name.split()[0],
                    "last_name": order.shipping_address.full_name.split()[-1],
                    "email": request.user.email,
                    "phone_number": order.shipping_address.phone,
                    "country": order.shipping_address.country,
                }
            }

            headers = {
                "Authorization": f"Token {paymob_secret_key}",
                "Content-Type": "application/json"
            }

            # إرسال الطلب لـ Paymob Intention API
            response = requests.post(
                "https://accept.paymob.com/v1/intention/",
                json=payload,
                headers=headers
            )

            if response.status_code != 201 and response.status_code != 200:
                print(response.json())
                return Response({"error": "Failed to create payment intention"}, status=status.HTTP_400_BAD_REQUEST)
            
            data = response.json()
            
            payment_methods = '--'.join([method['name'] for method in data.get('payment_methods', [])])
            # إنشاء Payment object في النظام
            payment = Payment.objects.create(
                user=request.user,
                order=order,
                amount=order.total_price,
                currency=order.currency,
                status="pending",
                provider="Paymob",
                provider_payment_id=data.get("id"),
                paymob_order_id=data.get("intention_order_id"),
                client_secret=data.get("client_secret"),
                payment_method=payment_methods,
                payment_url=f"https://accept.paymob.com/unifiedcheckout/?publicKey={settings.PAYMOB_PUBLIC_KEY}&clientSecret={data.get('client_secret')}"
            )

            order.payment_status = "pending"
            order.save()

            return Response({
                "payment_url": payment.payment_url,
            }, status=status.HTTP_201_CREATED)

        # طرق دفع أخرى يمكن إضافتها هنا
        return Response({"error": "Unsupported payment method"}, status=status.HTTP_400_BAD_REQUEST)

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib

@method_decorator(csrf_exempt, name='dispatch')
class PaymobCallbackView(APIView):
    """
    Handles Paymob webhook callback for transaction updates.
    """

    def post(self, request):
        data = request.data
        obj = data.get("obj", {})

        keys = {
            "amount_cents": obj.get("amount_cents"),
            "created_at": obj.get("created_at"),
            "currency": obj.get("currency"),
            "error_occured": obj.get("error_occured"),
            "has_parent_transaction": obj.get("has_parent_transaction"),
            "obj.id": obj.get("id"),
            "integration_id": obj.get("integration_id"),
            "is_3d_secure": obj.get("is_3d_secure"),
            "is_auth": obj.get("is_auth"),
            "is_capture": obj.get("is_capture"),
            "is_refunded": obj.get("is_refunded"),
            "is_standalone_payment": obj.get("is_standalone_payment"),
            "is_voided": obj.get("is_voided"),
            "order.id": obj.get("order", {}).get("id"),
            "owner": obj.get("owner"),
            "pending": obj.get("pending"),
            "source_data.pan": obj.get("source_data", {}).get("pan"),
            "source_data.sub_type": obj.get("source_data", {}).get("sub_type"),
            "source_data.type": obj.get("source_data", {}).get("type"),
            "success": obj.get("success"),
        }

        # Extract query parameters from URL
        received_hmac = request.query_params.get("hmac")

        if not received_hmac:
            print("HMAC missing in callback")
            return Response({"message": "HMAC missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Sort params alphabetically and concatenate values
        concatenated_string = "".join([str(keys[k]) for k in keys.keys()])

        # Compute HMAC using your Paymob HMAC secret
        computed_hmac = hmac.new(
            settings.PAYMOB_HMAC_SECRET.encode("utf-8"),  # Use the HMAC secret from settings
            concatenated_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()

        # Constant-time comparison
        if not hmac.compare_digest(computed_hmac, received_hmac):
            print("Invalid HMAC in callback")
            return Response({"message": "Invalid HMAC"}, status=status.HTTP_400_BAD_REQUEST)

        if data.get("type") != "TRANSACTION":
            print("Not a transaction callback")
            return Response({"message": "Not a transaction callback"}, status=status.HTTP_400_BAD_REQUEST)

        paymob_order_id = obj.get("order", {}).get("id")
        success = obj.get("success", False)

        payment = Payment.objects.filter(paymob_order_id=paymob_order_id).first()
        if not payment:
            print("Payment not found for order ID:", paymob_order_id)
            return Response({"message": "Payment not found"}, status=status.HTTP_202_ACCEPTED)

        payment.webhook_received = True
        payment.webhook_payload = data
        payment.save()

        order = payment.order
        if not order:
            print("Order not found for payment ID:", payment.id)
            return Response({"message": "Order not found"}, status=status.HTTP_202_ACCEPTED)

        if order.is_paid:
            print("Order already marked as paid:", order.order_number)
            return Response({"message": "Order already marked as paid"}, status=status.HTTP_200_OK)

        if success:
            print("Payment successful for order:", order.order_number)
            order.set_status("paid")
            payment.mark_as_paid()
            print("Order marked as paid:", order.order_number)
        else:
            print("Payment failed for order:", order.order_number)
            payment.mark_as_failed()

        print("Callback processed successfully for order:", order.order_number)
        return Response({"message": "Callback processed successfully"}, status=status.HTTP_200_OK)
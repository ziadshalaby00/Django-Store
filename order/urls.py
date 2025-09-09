from django.urls import path
from .views import (
    CreateOrderAPIView,
    UserOrdersAPIView,
    PaymentMethodsAPIView,
    EditOrderPaymentAPIView,
)

urlpatterns = [
    path("create-order/", CreateOrderAPIView.as_view(), name="create-order"),
    path('get-orders/', UserOrdersAPIView.as_view(), name='user-orders'),
    path('edit-order-payment/<int:order_id>/', EditOrderPaymentAPIView.as_view(), name='edit-order-payment'),
    path('payment-methods/', PaymentMethodsAPIView.as_view(), name='payment-methods'),
]

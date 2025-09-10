from django.urls import path
from .views import (
    CreateOrderAPIView,
    UserOrdersAPIView,
    PaymentMethodsAPIView,
)

urlpatterns = [
    path("create-order/", CreateOrderAPIView.as_view(), name="create-order"),
    path('get-orders/', UserOrdersAPIView.as_view(), name='user-orders'),
    path('payment-methods/', PaymentMethodsAPIView.as_view(), name='payment-methods'),
]

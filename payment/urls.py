# payments/urls.py
from django.urls import path
from .views import (
    CreatePaymentView,
    PaymobCallbackView,
)

urlpatterns = [
    path('create-payment/<int:order_id>/', CreatePaymentView.as_view(), name='create-payment'),
    path('paymob-callback/', PaymobCallbackView.as_view(), name='paymob-callback'),
]
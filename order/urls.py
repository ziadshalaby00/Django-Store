from django.urls import path
from .views import (
    CreateOrderAPIView,
    UserOrdersAPIView
)

urlpatterns = [
    path("create-order/", CreateOrderAPIView.as_view(), name="create-order"),
    path('get-orders/', UserOrdersAPIView.as_view(), name='user-orders'),
]

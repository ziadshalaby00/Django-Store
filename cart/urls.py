from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveFromCartView,
    ClearCartView,
)

urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("add/", AddToCartView.as_view(), name="cart-add"),
    path("update/<int:pk>/", UpdateCartItemView.as_view(), name="cart-update"),
    path("remove/<int:pk>/", RemoveFromCartView.as_view(), name="cart-remove"),
    path("clear/", ClearCartView.as_view(), name="cart-clear"),
]

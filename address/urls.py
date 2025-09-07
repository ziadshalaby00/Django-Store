from django.urls import path
from .views import UserAddressAPIView

urlpatterns = [
    path("address/", UserAddressAPIView.as_view(), name="user-address"),
]
from django.urls import path
from .views import (
    ProductReviewAPIView,
)

urlpatterns = [
    path("products/reviews/", ProductReviewAPIView.as_view(), name="user-reviews"),
    path("products/<int:product_id>/reviews/", ProductReviewAPIView.as_view(), name="product-reviews"),
]
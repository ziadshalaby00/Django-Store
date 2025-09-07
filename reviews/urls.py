from django.urls import path
from .views import (
    ProductReviewAPIView,
)

urlpatterns = [
    # GET كل الريفيوز الخاصة باليوزر
    path("products/reviews/", ProductReviewAPIView.as_view(), name="user-reviews"),
    # CRUD خاص بمنتج محدد
    path("products/<int:product_id>/reviews/", ProductReviewAPIView.as_view(), name="product-reviews"),
]
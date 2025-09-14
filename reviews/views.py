from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Review
from .serializers import ReviewSerializer, UserReviewSerializer
from product.models import Product
from rest_framework.pagination import PageNumberPagination

class ProductReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id=None):
        if product_id:
            queryset = Review.objects.filter(product_id=product_id).order_by('-created_at')
            serializer_class = ReviewSerializer
        else:
            queryset = Review.objects.filter(user=request.user).order_by('-created_at')
            serializer_class = UserReviewSerializer

        # ---- Pagination ----
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = serializer_class(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if Review.objects.filter(product_id=product_id, user=request.user).exists():
            raise ValidationError({"detail": "You have already reviewed this product."})

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, product_id):
        try:
            review = Review.objects.get(user=request.user, product_id=product_id)
        except Review.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, product_id):
        try:
            review = Review.objects.get(user=request.user, product_id=product_id)
        except Review.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response(
            {"detail": "Your review has been deleted successfully."},
            status=status.HTTP_200_OK
        )

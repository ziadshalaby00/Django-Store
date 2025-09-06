from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from .models import Category, Brand
from .serializers import CategorySerializer, BrandSerializer

class ProductListView(APIView):
    """
    GET parameters:
    - id: get product by id
    - category: filter by category id
    - brand: filter by brand id
    - min_price, max_price: filter by price_after_discount range
    - name: filter by name contains
    - description: filter by description contains
    """

    def get(self, request):
        queryset = Product.objects.filter(is_active=True)

        # فلترة حسب Category
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # فلترة حسب Brand
        brand_id = request.query_params.get('brand')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
            
        # فلترة حسب Name أو Description
        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # فلترة حسب Price بعد الخصم (خاصية محسوبة)
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            queryset = [p for p in queryset if p.price_after_discount >= float(min_price)]
        if max_price:
            queryset = [p for p in queryset if p.price_after_discount <= float(max_price)]

        # Sorting
        ordering = request.query_params.get('ordering')  # مثال: 'price' أو '-created_at'
        if ordering:
            if ordering.lstrip('-') == 'price':
                reverse = ordering.startswith('-')
                queryset = sorted(queryset, key=lambda p: p.price_after_discount, reverse=reverse)
            elif ordering.lstrip('-') == 'created_at':
                reverse = ordering.startswith('-')
                queryset = sorted(queryset, key=lambda p: p.created_at, reverse=reverse)

        # Pagination
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class ProductDetailView(APIView):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class BrandListView(APIView):
    def get(self, request):
        brands = Brand.objects.all()
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)
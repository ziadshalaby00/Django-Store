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
from .serializers import CategorySerializer, BrandSerializer, ProductDetailSerializer

from django.db.models import F, ExpressionWrapper, DecimalField

class ProductListView(APIView):
    """
    GET parameters:
    - category: filter by category id
    - brand: filter by brand id
    - min_price, max_price: filter by price_after_discount range
    - search: filter by name or description contains
    - ordering: 'price' or '-price' or 'created_at' or '-created_at'
    - page: page number for pagination
    """

    def get(self, request):
        queryset = Product.objects.filter(is_active=True)

        # ---- Filters ----
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        brand_id = request.query_params.get('brand')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Annotate price_after_discount (price * (1 - discount/100))
        queryset = queryset.annotate(
            price_after_discount_value=ExpressionWrapper(
                F("price") * (1 - F("discount_percentage") / 100.0),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        # min_price & max_price
        min_price = request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price_after_discount_value__gte=min_price)

        max_price = request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price_after_discount_value__lte=max_price)

        # ---- Ordering ----
        ordering = request.query_params.get('ordering')
        if ordering:
            if ordering.lstrip('-') in ['price', 'created_at']:
                if ordering.lstrip('-') == 'price':
                    ordering = ordering.replace('price', 'price_after_discount_value')
                queryset = queryset.order_by(ordering)

        # ---- Pagination ----
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        serializer = ProductDetailSerializer(product)
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
from django.urls import path
from .views import (
    ProductListView,
    CategoryListView,
    BrandListView,
    ProductDetailView,
)

urlpatterns = [
    path('get-products/', ProductListView.as_view(), name='product_list'),
    path('get-products/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    
    path('get-categories/', CategoryListView.as_view(), name='category_list'),
    path('get-brands/', BrandListView.as_view(), name='brand_list'),
]
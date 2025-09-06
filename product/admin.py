from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Brand, Category, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'price_before_discount', 'discount_percentage', 'price_after_discount',
        'stock', 'brand', 'category', 'is_active', 'created_by', 'created_at'
    )
    list_filter = ('brand', 'category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('price_before_discount', 'price_after_discount')
    autocomplete_fields = ('brand', 'category', 'created_by')
    ordering = ('-created_at',)
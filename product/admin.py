from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Brand, Category, Product, ProductImage


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image', 'created_at')
    search_fields = ('product',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'short_name', 'price', 'discount_percentage', 'price_after_discount',
        'stock', 'is_active', 'created_by', 'brand', 'category', 'created_at'
    )
    list_filter = ('brand', 'category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('price_after_discount',)
    autocomplete_fields = ('brand', 'category', 'created_by')
    ordering = ('-created_at',)

    def short_name(self, obj):
        return obj.name[:50] + "..." if len(obj.name) > 50 else obj.name
    short_name.short_description = "Name"

    inlines = [ProductImageInline]
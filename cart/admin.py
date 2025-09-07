from django.contrib import admin

# Register your models here.
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_items", "total_price", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "subtotal")
    search_fields = ("product__name", "cart__user__username")
    list_filter = ("product",)

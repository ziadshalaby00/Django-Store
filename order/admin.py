from django.contrib import admin

# Register your models here.
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("product", "quantity", "price_at_purchase", "subtotal_display")
    extra = 0

    def subtotal_display(self, obj):
        return f"{obj.subtotal} {obj.order.currency}"
    subtotal_display.short_description = "Subtotal"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_number", "user", "total_price", "currency", "payment_status", "is_paid", "payment_method", "created_at")
    list_filter = ("payment_status", "payment_method", "created_at")
    search_fields = ("user__username", "user__email", "order_number", "id")
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price_at_purchase", "subtotal_display")
    readonly_fields = ("subtotal_display",)

    def subtotal_display(self, obj):
        return f"{obj.subtotal} {obj.order.currency}"
    subtotal_display.short_description = "Subtotal"
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "amount",
        "currency",
        "status",
        "provider",
        "provider_payment_id",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "currency", "provider", "created_at")
    search_fields = ("order__id", "provider_payment_id", "provider")
    ordering = ("-created_at",)

    # الحقول اللي تتعرض بس (read-only)
    readonly_fields = ("currency", "created_at", "updated_at")

    fieldsets = (
        (None, {
            "fields": ("order", "amount", "currency", "status")
        }),
        ("Provider Info", {
            "fields": ("provider", "provider_payment_id"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )
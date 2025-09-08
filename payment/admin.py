# payments/admin.py
from django.contrib import admin
from .models import Payment
from django.utils.html import format_html
import json

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "user",
        "amount",
        "currency",
        "status",
        "is_paid",
        "payment_method",
        "provider",
        "provider_payment_id",
        "created_at",
    )
    
    def webhook_payload_display(self, obj):
        if not obj.webhook_payload:
            return "-"
        formatted_json = json.dumps(obj.webhook_payload, indent=2)
        return format_html(
            "<details style='max-width:600px;'><summary>Show JSON</summary><pre>{}</pre></details>",
            formatted_json
        )
    webhook_payload_display.short_description = "Webhook Payload"
    
    list_filter = (
        "status",
        "payment_method",
        "provider",
        "is_paid",
        "created_at",
    )
    search_fields = (
        "order__order_number",
        "user__username",
        "provider_payment_id",
        "payment_method",
    )
    readonly_fields = (
        "client_secret",
        "payment_url",
        "webhook_received",
        "webhook_payload_display",
        "created_at",
        "updated_at",
    )
    exclude = ("webhook_payload",)
    ordering = ("-created_at",)
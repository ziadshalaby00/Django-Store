from django.contrib import admin

# Register your models here.
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at", "product")
    search_fields = ("product__name", "user__username", "comment")
    ordering = ("-created_at",)

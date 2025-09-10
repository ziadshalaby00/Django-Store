from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # نعدل على fieldsets بالكامل بدل + 
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("fullname", "email", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("User Stats", {"fields": ("total_spent_display", "total_orders_display", "total_products_display")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "fullname", "email", "password1", "password2"),
        }),
    )

    list_display = ["username", "email", "fullname", "is_staff", "is_active"]

    readonly_fields = ("total_spent_display", "total_orders_display", "total_products_display")

    def total_spent_display(self, obj):
        return obj.total_spent
    total_spent_display.short_description = "Total Spent"

    def total_orders_display(self, obj):
        return obj.total_orders
    total_orders_display.short_description = "Total Orders"

    def total_products_display(self, obj):
        return obj.total_products
    total_products_display.short_description = "Total Products"


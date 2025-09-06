from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("fullname",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("fullname",)}),
    )
    list_display = ["username", "email", "fullname", "is_staff", "is_active"]
    search_fields = ["username", "email", "fullname"]
    ordering = ["username"]
from django.contrib import admin

# Register your models here.
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "street", "city", "country", "phone")
    list_filter = ("country", "city")
    search_fields = ("full_name", "street", "city", "user__username", "user__email")

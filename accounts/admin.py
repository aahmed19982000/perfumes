# apps/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer, Address, Governorate, City


@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ["name_ar", "name_en", "is_active"]
    list_editable = ["is_active"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name_ar", "name_en", "governorate", "shipping_cost", "is_active"]
    list_filter = ["governorate", "is_active"]
    list_editable = ["shipping_cost", "is_active"]


class AddressInline(admin.TabularInline):
    model  = Address
    extra  = 0
    fields = ["full_name", "phone", "governorate", "city", "street", "is_default"]


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    model               = Customer
    list_display        = ["email", "get_full_name", "phone", "is_active", "created_at"]
    list_filter         = ["is_active", "is_staff"]
    search_fields       = ["email", "first_name", "last_name", "phone"]
    ordering            = ["-created_at"]
    inlines             = [AddressInline]

    fieldsets = (
        ("بيانات الدخول",  {"fields": ("email", "password")}),
        ("البيانات الشخصية", {"fields": ("first_name", "last_name", "phone", "avatar")}),
        ("الصلاحيات",      {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("التواريخ",       {"fields": ("last_login", "created_at")}),
    )
    readonly_fields     = ["created_at", "last_login"]
    add_fieldsets       = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "first_name", "last_name", "phone", "password1", "password2"),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "customer", "governorate", "city", "is_default"]
    list_filter   = ["governorate", "is_default"]
    search_fields = ["full_name", "phone", "customer__email"]
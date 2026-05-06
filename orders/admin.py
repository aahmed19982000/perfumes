# apps/orders/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model           = CartItem
    extra           = 0
    readonly_fields = ["unit_price", "line_total"]
    fields          = ["product", "quantity", "unit_price", "line_total"]

    def unit_price(self, obj):
        return f"L.E {obj.unit_price}"
    unit_price.short_description = "سعر الوحدة"

    def line_total(self, obj):
        return f"L.E {obj.line_total}"
    line_total.short_description = "الإجمالي"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display    = ["customer", "total_items", "subtotal_display", "updated_at"]
    readonly_fields = ["total_items", "subtotal_display", "created_at", "updated_at"]
    inlines         = [CartItemInline]

    def subtotal_display(self, obj):
        return f"L.E {obj.subtotal}"
    subtotal_display.short_description = "المجموع"







class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ["product_name", "product_sku", "unit_price", "quantity", "line_total"]
    fields          = ["product_name", "product_sku", "unit_price", "quantity", "line_total"]

    def line_total(self, obj):
        return f"L.E {obj.line_total}"
    line_total.short_description = "الإجمالي"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ["order_number", "customer", "status_badge", "payment_method",
                       "total_display", "is_paid", "created_at"]
    list_filter     = ["status", "payment_method", "is_paid", "created_at"]
    search_fields   = ["order_number", "customer__email", "shipping_phone", "shipping_full_name"]
    readonly_fields = ["order_number", "subtotal", "total", "created_at", "updated_at"]
    list_editable   = ["is_paid"]
    inlines         = [OrderItemInline]

    fieldsets = (
        ("رقم الطلب",   {"fields": ("order_number",)}),
        ("العميل",      {"fields": ("customer",)}),
        ("بيانات الشحن", {"fields": ("shipping_full_name", "shipping_phone",
                                     "shipping_governorate", "shipping_city",
                                     "shipping_street", "shipping_building")}),
        ("المبالغ",     {"fields": ("subtotal", "shipping_cost", "discount_amount", "total", "coupon_code")}),
        ("الدفع",       {"fields": ("payment_method", "is_paid", "paid_at")}),
        ("الحالة",      {"fields": ("status", "notes")}),
        ("التواريخ",    {"fields": ("created_at", "updated_at")}),
    )

    def status_badge(self, obj):
        return format_html(
            '<span style="color:#fff;background:{};padding:3px 10px;'
            'border-radius:10px;font-size:11px">{}</span>',
            obj.status_badge_color,
            obj.get_status_display(),
        )
    status_badge.short_description = "الحالة"

    def total_display(self, obj):
        return f"L.E {obj.total}"
    total_display.short_description = "الإجمالي"
# apps/wishlist/admin.py

from django.contrib import admin
from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model          = WishlistItem
    extra          = 0
    readonly_fields = ["product", "added_at"]
    fields         = ["product", "added_at"]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display    = ["customer", "total_items", "created_at"]
    readonly_fields = ["total_items", "created_at"]
    inlines         = [WishlistItemInline]

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = "عدد المنتجات"


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display  = ["product", "wishlist", "added_at"]
    list_filter   = ["added_at"]
    search_fields = ["product__name_ar", "wishlist__customer__email"]
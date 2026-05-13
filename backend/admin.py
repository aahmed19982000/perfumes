from django.contrib import admin
from .models import HeaderSettings


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("البيانات الأساسية", {
            "fields": ("phone_number", "logo_text", "logo_accent"),
        }),
        ("إظهار وإخفاء عناصر الهيدر", {
            "fields": (
                "show_top_bar", "show_phone", "show_language_switcher",
                "show_search", "show_wishlist", "show_cart",
            ),
        }),
        ("البحث", {
            "fields": (
                "search_placeholder_ar", "search_placeholder_en",
                "mobile_search_placeholder_ar", "mobile_search_placeholder_en",
            ),
        }),
        ("روابط الهيدر", {
            "fields": (
                "show_home_link", "home_label_ar", "home_label_en",
                "show_categories_link", "categories_label_ar", "categories_label_en",
                "categories_menu_title_ar", "categories_menu_title_en",
                "show_offers_link", "offers_label_ar", "offers_label_en",
                "show_brands_link", "brands_label_ar", "brands_label_en",
                "show_track_order_link", "track_order_label_ar", "track_order_label_en",
                "show_about_link", "about_label_ar", "about_label_en",
            ),
        }),
    )

    def has_add_permission(self, request):
        return not HeaderSettings.objects.exists()

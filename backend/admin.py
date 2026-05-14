from django.contrib import admin
from .models import HeaderSettings, FooterSettings


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("اللوجو والهوية", {
            "fields": ("logo_text", "logo_accent", "logo_image", "favicon"),
        }),
        ("البيانات الأساسية", {
            "fields": ("phone_number",),
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


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("اللوجو", {
            "fields": ("logo_text", "logo_accent"),
        }),
        ("النصوص التعريفية", {
            "fields": ("tagline_ar", "tagline_en", "about_text_ar", "about_text_en"),
        }),
        ("روابط التواصل الاجتماعي", {
            "fields": ("fb_link", "insta_link", "wa_link", "tiktok_link"),
        }),
        ("معلومات التواصل", {
            "fields": (
                "phone", "email", "working_hours_ar", "working_hours_en",
                "address_ar", "address_en",
            ),
        }),
        ("حقوق النشر", {
            "fields": ("copyright_text_ar", "copyright_text_en"),
        }),
    )

    def has_add_permission(self, request):
        return not FooterSettings.objects.exists()

# banners/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display  = ["preview", "title_ar", "position", "order", "is_active", "created_at"]
    list_filter   = ["position", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["title_ar", "title_en"]

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:6px;object-fit:cover"/>',
                obj.image.url,
            )
        return "—"
    preview.short_description = "معاينة"
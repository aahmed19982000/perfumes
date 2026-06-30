# apps/products/admin.py

from django.contrib import admin
from .models import Category, SubCategory , Brand


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    fields = ["name_ar", "name_en", "slug", "image", "is_active"]
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ["name_ar", "name_en", "slug", "is_active", "created_at"]
    list_filter   = ["is_active"]
    search_fields = ["name_ar", "name_en"]
    prepopulated_fields = {"slug": ("name_en",)}
    inlines = [SubCategoryInline]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display  = ["name_ar", "category", "slug", "is_active"]
    list_filter   = ["category", "is_active"]
    search_fields = ["name_ar", "name_en"]
    prepopulated_fields = {"slug": ("name_en",)}



@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display        = ["name", "slug", "product_count", "is_active", "created_at"]
    list_filter         = ["is_active"]
    search_fields       = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable       = ["is_active"]

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "عدد المنتجات"




# apps/products/admin.py  —  أضف للملف الموجود

from django.utils.html import format_html
from .models import Category, SubCategory, Brand, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model   = ProductImage
    extra   = 3
    fields  = ["image", "preview", "alt_text", "is_main", "order"]
    readonly_fields = ["preview"]

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:6px"/>', obj.image.url)
        return "—"
    preview.short_description = "معاينة"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display    = ["thumbnail_preview", "name_ar", "brand", "category", "size",
                       "price", "final_price_display", "stock", "stock_badge",
                       "is_featured", "is_active"]
    list_filter     = ["category", "sub_category", "brand", "is_active", "is_featured"]
    search_fields   = ["name_ar", "name_en", "sku", "slug"]
    list_editable   = ["price", "stock", "is_featured", "is_active"]
    readonly_fields = ["sku", "slug", "created_at", "updated_at",
                       "avg_rating", "review_count", "thumbnail_preview"]
    prepopulated_fields = {}   # slug يتولد تلقائي في save()
    inlines         = [ProductImageInline]

    fieldsets = (
        ("المعرّف",        {"fields": ("sku", "slug")}),
        ("الأسماء والوصف", {"fields": ("name_ar", "name_en", "size", "concentration", "description_ar", "description_en")}),
        ("التصنيف",        {"fields": ("category", "sub_category", "brand")}),
        ("السعر والمخزون", {"fields": ("price", "discount_price", "stock")}),
        ("الصورة",         {"fields": ("thumbnail", "thumbnail_preview")}),
        ("الحالة",         {"fields": ("is_active", "is_featured")}),
        ("الإحصاءات",      {"fields": ("avg_rating", "review_count", "created_at", "updated_at")}),
    )

    # ── عمود الصورة المصغرة في القائمة ──────────────────────────
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height:50px;border-radius:6px"/>', obj.thumbnail.url)
        return "—"
    thumbnail_preview.short_description = "صورة"

    # ── عمود السعر النهائي ───────────────────────────────────────
    def final_price_display(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="color:#e74c3c;font-weight:bold">L.E {}</span>'
                ' <small style="text-decoration:line-through;color:#999">L.E {}</small>',
                obj.discount_price, obj.price
            )
        return f"L.E {obj.price}"
    final_price_display.short_description = "السعر الفعلي"

    # ── شارة المخزون ─────────────────────────────────────────────
    def stock_badge(self, obj):
        if obj.is_out_of_stock:
            return format_html('<span style="color:#fff;background:#e74c3c;padding:2px 8px;border-radius:10px;font-size:11px">نفد</span>')
        if obj.stock <= 5:
            return format_html('<span style="color:#fff;background:#f39c12;padding:2px 8px;border-radius:10px;font-size:11px">قليل</span>')
        return format_html('<span style="color:#fff;background:#27ae60;padding:2px 8px;border-radius:10px;font-size:11px">متاح</span>')
    stock_badge.short_description = "حالة المخزون"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["preview", "product", "is_main", "order"]
    list_filter  = ["is_main"]

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:6px"/>', obj.image.url)
        return "—"
    preview.short_description = "معاينة"
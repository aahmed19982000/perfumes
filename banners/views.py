# core/views.py  —  الصفحة الرئيسية مع البانرات والأقسام

from django.shortcuts import render
from banners.models import Banner
from products.models import Product, Category, Brand


def home_view(request):
    context = {
        # ── البانرات ──────────────────────────────────────────────
        "hero_banners": Banner.objects.filter(
            position=Banner.Position.HERO,
            is_active=True,
        ).order_by("order"),

        "secondary_banners": Banner.objects.filter(
            position=Banner.Position.SECONDARY,
            is_active=True,
        ).order_by("order"),

        # ── المنتجات ──────────────────────────────────────────────
        "latest_products": Product.objects.filter(
            is_active=True
        ).order_by("-created_at")[:8],

        "featured_products": Product.objects.filter(
            is_active=True, is_featured=True
        ).order_by("-created_at")[:8],

        "best_selling": Product.objects.filter(
            is_active=True
        ).order_by("-order_items__quantity")[:8],

        # ── الفئات والبراندات ─────────────────────────────────────
        "categories": Category.objects.filter(is_active=True),
        "brands":     Brand.objects.filter(is_active=True)[:15],
    }
    return render(request, "home/index.html", context)
# core/views.py

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from banners.models import Banner
from products.models import Product, Category, Brand
from .dashboard import get_dashboard_stats


def home_view(request):
    context = {
        "hero_banners": Banner.objects.filter(
            position=Banner.Position.HERO,
            is_active=True,
        ).order_by("order"),

        "secondary_banners": Banner.objects.filter(
            position=Banner.Position.SECONDARY,
            is_active=True,
        ).order_by("order"),

        "latest_products": Product.objects.filter(
            is_active=True
        ).order_by("-created_at")[:8],

        "featured_products": Product.objects.filter(
            is_active=True, is_featured=True
        ).order_by("-created_at")[:8],

        "categories": Category.objects.filter(is_active=True),
        "brands":     Brand.objects.filter(is_active=True)[:15],
    }
    return render(request, "home/index.html", context)


@staff_member_required
def admin_dashboard(request):
    stats = get_dashboard_stats()
    return render(request, "admin/dashboard.html", stats)
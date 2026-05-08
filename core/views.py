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


def about_view(request):
    return render(request, "pages/about.html")

def faq_view(request):
    return render(request, "pages/faq.html")

def privacy_view(request):
    return render(request, "pages/privacy.html")

def terms_view(request):
    return render(request, "pages/terms.html")


def offers_view(request):
    from django.db.models import F, ExpressionWrapper, DecimalField
    products = Product.objects.filter(
        is_active=True,
        discount_price__isnull=False,
    ).order_by("-created_at")

    sort = request.GET.get("sort", "discount")
    if sort == "price_asc":
        products = products.order_by("discount_price")
    elif sort == "price_desc":
        products = products.order_by("-discount_price")
    else:
        products = products.order_by("-created_at")

    categories = Category.objects.filter(is_active=True)
    cat_id = request.GET.get("category")
    if cat_id:
        products = products.filter(category_id=cat_id)

    context = {
        "products": products,
        "categories": categories,
        "current_sort": sort,
        "current_cat": int(cat_id) if cat_id else None,
        "total_count": products.count(),
    }
    return render(request, "home/offers.html", context)


def brands_view(request):
    from django.db.models import Count, Q
    brands = Brand.objects.filter(is_active=True).order_by("name").annotate(
        num_products=Count('products', filter=Q(products__is_active=True))
    )
    context = {
        "brands": brands,
        "total_count": brands.count(),
    }
    return render(request, "home/brands.html", context)
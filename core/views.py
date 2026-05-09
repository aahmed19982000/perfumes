# core/views.py

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from banners.models import Banner
from products.models import Product, Category, Brand
from .dashboard import get_dashboard_stats
from orders.models import Offer
from django.utils import timezone



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
    from orders.models import Offer
    from django.utils import timezone
    now = timezone.now()
    offers = Offer.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_to__gte=now,
    ).prefetch_related('eligible_products', 'eligible_categories')

    return render(request, 'home/offers.html', {'offers': offers})

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
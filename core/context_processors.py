# core/context_processors.py

from products.models import Category, Brand


def nav_context(request):
    return {
        "nav_categories": Category.objects.filter(
            is_active=True
        ).prefetch_related("sub_categories"),

        "nav_brands": Brand.objects.filter(
            is_active=True
        )[:10],
    }
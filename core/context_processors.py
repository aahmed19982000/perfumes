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


def shop_context(request):
    context = {
        "cart_count": 0,
        "wishlist_count": 0,
    }
    if request.user.is_authenticated:
        try:
            context["cart_count"] = request.user.cart.total_items
        except:
            pass
        try:
            context["wishlist_count"] = request.user.wishlist.total_items
        except:
            pass
    return context
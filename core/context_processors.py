# core/context_processors.py

from products.models import Category, Brand
from backend.models import HeaderSettings, FooterSettings


def nav_context(request):
    try:
        header_settings = HeaderSettings.load()
    except Exception:
        header_settings = None

    try:
        footer_settings = FooterSettings.load()
    except Exception:
        footer_settings = None

    return {
        "nav_categories": Category.objects.filter(
            is_active=True
        ).prefetch_related("sub_categories"),

        "nav_brands": Brand.objects.filter(
            is_active=True
        )[:10],

        "is_en": request.LANGUAGE_CODE == "en",
        "header_settings": header_settings,
        "footer_settings": footer_settings,
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
    else:
        # للضيوف
        session_cart = request.session.get('cart', {})
        context["cart_count"] = sum(session_cart.values())
        
        session_wishlist = request.session.get('wishlist', [])
        context["wishlist_count"] = len(session_wishlist)
        
    return context

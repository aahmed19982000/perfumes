# apps/wishlist/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Wishlist, WishlistItem
from products.models import Product


def get_or_create_wishlist(user):
    wishlist, _ = Wishlist.objects.get_or_create(customer=user)
    return wishlist


# ── عرض قائمة الأمنيات ───────────────────────────────────────────
@login_required
def wishlist_view(request):
    wishlist = get_or_create_wishlist(request.user)
    return render(request, "wishlist/wishlist.html", {"wishlist": wishlist})


# ── إضافة / حذف (toggle) من الأمنيات (AJAX) ─────────────────────
@require_POST
@login_required
def toggle_wishlist(request, product_id):
    product  = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist = get_or_create_wishlist(request.user)

    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
    )

    if not created:
        item.delete()
        return JsonResponse({
            "status":       "removed",
            "message":      "تم الحذف من قائمة الأمنيات",
            "wishlist_count": wishlist.total_items,
        })

    return JsonResponse({
        "status":         "added",
        "message":        "تمت الإضافة لقائمة الأمنيات",
        "wishlist_count": wishlist.total_items,
    })


# ── حذف مباشر من صفحة الأمنيات ──────────────────────────────────
@require_POST
@login_required
def remove_from_wishlist(request, item_id):
    item     = get_object_or_404(WishlistItem, id=item_id, wishlist__customer=request.user)
    wishlist = item.wishlist
    item.delete()

    return JsonResponse({
        "status":         "removed",
        "wishlist_count": wishlist.total_items,
    })


# ── نقل منتج من الأمنيات للسلة ───────────────────────────────────
@require_POST
@login_required
def move_to_cart(request, item_id):
    item    = get_object_or_404(WishlistItem, id=item_id, wishlist__customer=request.user)
    product = item.product

    if product.is_out_of_stock:
        return JsonResponse({"status": "error", "message": "المنتج نفد من المخزون"}, status=400)

    from orders.models import Cart, CartItem
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={"quantity": 1},
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    item.delete()

    return JsonResponse({
        "status":         "moved",
        "message":        "تم النقل للسلة",
        "cart_count":     cart.total_items,
        "wishlist_count": item.wishlist.total_items,
    })
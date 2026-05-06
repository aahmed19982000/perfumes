# apps/wishlist/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Wishlist, WishlistItem
from products.models import Product


def get_wishlist_data(request):
    """
    يوحد التعامل مع قائمة الأمنيات للمسجلين والضيوف
    """
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(customer=request.user)
        items = []
        for item in wishlist.items.select_related('product'):
            items.append({
                'id': item.id,
                'product': item.product,
            })
        return {
            'items': items,
            'total_items': wishlist.total_items,
            'is_empty': wishlist.is_empty,
        }
    else:
        session_wishlist = request.session.get('wishlist', [])
        items = []
        for p_id in session_wishlist:
            product = Product.objects.filter(id=p_id, is_active=True).first()
            if product:
                items.append({
                    'id': p_id,
                    'product': product,
                })
        return {
            'items': items,
            'total_items': len(items),
            'is_empty': not items,
        }


def wishlist_view(request):
    wishlist_data = get_wishlist_data(request)
    return render(request, "wishlist/wishlist.html", {"wishlist": wishlist_data})


@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(customer=request.user)
        item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        if not created:
            item.delete()
            status = 'removed'
            msg = "تم الحذف من قائمة الأمنيات"
        else:
            status = 'added'
            msg = "تمت الإضافة لقائمة الأمنيات"
        wishlist_count = wishlist.total_items
    else:
        wishlist = request.session.get('wishlist', [])
        p_id = int(product_id)
        if p_id in wishlist:
            wishlist.remove(p_id)
            status = 'removed'
            msg = "تم الحذف من قائمة الأمنيات"
        else:
            wishlist.append(p_id)
            status = 'added'
            msg = "تمت الإضافة لقائمة الأمنيات"
        request.session['wishlist'] = wishlist
        request.session.modified = True
        wishlist_count = len(wishlist)

    return JsonResponse({
        "status": status,
        "message": msg,
        "wishlist_count": wishlist_count,
    })


@require_POST
def remove_from_wishlist(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(WishlistItem, id=item_id, wishlist__customer=request.user)
        wishlist = item.wishlist
        item.delete()
        wishlist_count = wishlist.total_items
    else:
        wishlist = request.session.get('wishlist', [])
        p_id = int(item_id)
        if p_id in wishlist:
            wishlist.remove(p_id)
            request.session['wishlist'] = wishlist
            request.session.modified = True
        wishlist_count = len(wishlist)

    return JsonResponse({
        "status": "removed",
        "wishlist_count": wishlist_count,
    })


@require_POST
def move_to_cart(request, item_id):
    # للتبسيط، في حالة الضيف item_id هو product_id
    if request.user.is_authenticated:
        item = get_object_or_404(WishlistItem, id=item_id, wishlist__customer=request.user)
        product = item.product
        item.delete()
        # إضافة للسلة (مسجل)
        from orders.models import Cart, CartItem
        cart, created = Cart.objects.get_or_create(customer=request.user)
        c_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity':1})
        if not created:
            c_item.quantity += 1
            c_item.save()
        cart_count = cart.total_items
        wish_count = Wishlist.objects.get(customer=request.user).total_items
    else:
        p_id = int(item_id)
        product = get_object_or_404(Product, id=p_id)
        wishlist = request.session.get('wishlist', [])
        if p_id in wishlist:
            wishlist.remove(p_id)
            request.session['wishlist'] = wishlist
            request.session.modified = True
        
        # إضافة للسلة (ضيف)
        cart = request.session.get('cart', {})
        cart[str(p_id)] = cart.get(str(p_id), 0) + 1
        request.session['cart'] = cart
        request.session.modified = True
        
        cart_count = sum(cart.values())
        wish_count = len(wishlist)

    return JsonResponse({
        "status": "moved",
        "message": "تم النقل للسلة",
        "cart_count": cart_count,
        "wishlist_count": wish_count,
    })
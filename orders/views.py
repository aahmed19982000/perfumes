# apps/orders/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
from .models import Cart, CartItem, Order
from products.models import Product
from django.contrib import messages
from .services import create_order_from_cart




def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(customer=user)
    return cart


# ── عرض السلة ────────────────────────────────────────────────────
@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    return render(request, "orders/cart.html", {"cart": cart})


# ── إضافة منتج للسلة (AJAX) ──────────────────────────────────────
@require_POST
@login_required
def add_to_cart(request, product_id):
    product  = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))
    
    # الترجمة للرسالة
    msg_success = _("تمت الإضافة للسلة") if request.LANGUAGE_CODE == 'ar' else "Added to cart"
    msg_oos     = _("المنتج نفد من المخزون") if request.LANGUAGE_CODE == 'ar' else "Product out of stock"

    if product.is_out_of_stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"status": "error", "message": msg_oos}, status=400)
        messages.error(request, msg_oos)
        return redirect("product_detail", slug=product.slug)

    cart = get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={"quantity": quantity},
    )

    if not created:
        item.quantity += quantity
        item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            "status":      "success",
            "message":     msg_success,
            "cart_count":  cart.total_items,
            "cart_total":  str(cart.subtotal),
        })
    
    messages.success(request, msg_success)
    next_url = request.GET.get("next")
    if next_url == "checkout":
        return redirect("checkout")
    return redirect("cart")


# ── تعديل الكمية (AJAX) ──────────────────────────────────────────
@require_POST
@login_required
def update_cart(request, item_id):
    item     = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    quantity = int(request.POST.get("quantity", 1))

    if quantity < 1:
        item.delete()
        return JsonResponse({"status": "removed"})

    if quantity > item.product.stock:
        return JsonResponse({"status": "error", "message": "الكمية تتجاوز المخزون"}, status=400)

    item.quantity = quantity
    item.save()

    return JsonResponse({
        "status":     "updated",
        "line_total": str(item.line_total),
        "cart_total": str(item.cart.subtotal),
        "cart_count": item.cart.total_items,
    })


# ── حذف منتج من السلة (AJAX) ─────────────────────────────────────
@require_POST
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    cart = item.cart
    item.delete()

    return JsonResponse({
        "status":     "removed",
        "cart_count": cart.total_items,
        "cart_total": str(cart.subtotal),
    })






@login_required
def checkout_view(request):
    cart = get_or_create_cart(request.user)
    if cart.is_empty:
        return redirect("cart")

    from accounts.models import Governorate, Address, City
    addresses    = request.user.addresses.all()
    governorates = Governorate.objects.filter(is_active=True)

    if request.method == "POST":
        address_id     = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method", "cod")
        notes          = request.POST.get("notes", "")

        # ── معالجة عنوان جديد ──────────────────────────────────────
        if not address_id and request.POST.get("new_full_name"):
            try:
                new_addr = Address.objects.create(
                    customer     = request.user,
                    full_name    = request.POST.get("new_full_name"),
                    phone        = request.POST.get("new_phone"),
                    governorate_id = request.POST.get("new_governorate"),
                    city_id        = request.POST.get("new_city"),
                    street       = request.POST.get("new_street"),
                    building     = request.POST.get("new_building"),
                    is_default   = request.POST.get("save_address") == "on"
                )
                address_id = new_addr.id
            except Exception as e:
                messages.error(request, f"خطأ في إنشاء العنوان: {str(e)}")

        if not address_id:
            messages.error(request, "يرجى اختيار عنوان الشحن") if request.LANGUAGE_CODE == 'ar' else messages.error(request, "Please select a shipping address")
        else:
            try:
                order = create_order_from_cart(
                    customer       = request.user,
                    address_id     = address_id,
                    payment_method = payment_method,
                    notes          = notes,
                )
                return redirect("order_success", order_number=order.order_number)
            except Exception as e:
                messages.error(request, str(e))

    return render(request, "orders/checkout.html", {
        "cart":         cart,
        "addresses":    addresses,
        "governorates": governorates,
    })


@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def order_list_view(request):
    orders = request.user.orders.prefetch_related("items").all()
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def cancel_order_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)

    if not order.can_cancel:
        messages.error(request, "لا يمكن إلغاء هذا الطلب في مرحلته الحالية")
        return redirect("order_detail", order_number=order_number)

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])
    messages.success(request, "تم إلغاء الطلب بنجاح")
    return redirect("order_list")


def track_order_view(request):
    order = None
    if request.method == "POST":
        order_number = request.POST.get("order_number", "").strip()
        order = Order.objects.filter(order_number=order_number).first()
        if not order:
            messages.error(request, "رقم الطلب غير صحيح")

    return render(request, "orders/track_order.html", {"order": order})
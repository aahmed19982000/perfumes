# apps/orders/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
from django.utils import timezone
from .models import Cart, CartItem, Order, Coupon
from products.models import Product
from django.contrib import messages
from .services import create_order_from_cart, OutOfStockError




def get_cart_data(request):
    from .services import apply_single_offer, get_available_offers_for_cart

    selected_offer_id = request.session.get('selected_offer_id')

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(customer=request.user)
        items = []
        for item in cart.items.select_related('product'):
            items.append({
                'id':         item.id,
                'product':    item.product,
                'quantity':   item.quantity,
                'unit_price': item.unit_price,
                'line_total': item.line_total,
            })

        subtotal        = cart.subtotal
        coupon_discount = cart.discount_amount
        coupon_code     = cart.coupon.code if cart.coupon else None

    else:
        session_cart = request.session.get('cart', {})
        items = []
        subtotal    = 0
        total_items = 0
        to_delete   = []

        for p_id, qty in session_cart.items():
            product = Product.objects.filter(id=p_id, is_active=True).first()
            if product:
                price      = product.final_price
                line_total = price * qty
                items.append({
                    'id':         p_id,
                    'product':    product,
                    'quantity':   qty,
                    'unit_price': price,
                    'line_total': line_total,
                })
                subtotal    += line_total
                total_items += qty
            else:
                to_delete.append(p_id)

        for p_id in to_delete:
            del session_cart[p_id]
        if to_delete:
            request.session.modified = True

        coupon_id       = request.session.get('coupon_id')
        coupon_discount = 0
        coupon_code     = None
        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id, active=True).first()
            if coupon:
                coupon_discount = (subtotal * coupon.discount) / 100
                coupon_code     = coupon.code

    # ── العروض المتاحة للاختيار ──────────────────────
    available_offers = get_available_offers_for_cart(items, subtotal)

    # ── تطبيق العرض المختار فقط ──────────────────────
    if selected_offer_id:
        offers_result = apply_single_offer(items, subtotal, selected_offer_id)
    else:
        offers_result = {
            'discount_amount': 0,
            'free_items':      [],
            'free_shipping':   False,
            'applied_offers':  [],
        }

    offers_discount = offers_result['discount_amount']
    total_discount  = coupon_discount + offers_discount

    base = {
        'items':            items,
        'subtotal':         subtotal,
        'coupon_discount':  coupon_discount,
        'offers_discount':  offers_discount,
        'discount_amount':  total_discount,
        'total':            max(subtotal - total_discount, 0),
        'coupon_code':      coupon_code,
        'is_empty':         not items,
        'free_items':       offers_result['free_items'],
        'free_shipping':    offers_result['free_shipping'],
        'applied_offers':   offers_result['applied_offers'],
        'available_offers': available_offers,
        'selected_offer_id': selected_offer_id,
    }

    if request.user.is_authenticated:
        base['total_items'] = cart.total_items
    else:
        base['total_items'] = total_items

    return base

def cart_view(request):
    cart_data = get_cart_data(request)
    return render(request, "orders/cart.html", {"cart": cart_data})


@require_POST
def add_to_cart(request, product_id):
    product  = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))
    
    msg_success = _("تمت الإضافة للسلة") if request.LANGUAGE_CODE == 'ar' else "Added to cart"
    msg_oos     = _("المنتج نفد من المخزون") if request.LANGUAGE_CODE == 'ar' else "Product out of stock"

    if product.is_out_of_stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"status": "error", "message": msg_oos}, status=400)
        messages.error(request, msg_oos)
        return redirect("product_detail", slug=product.slug)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(customer=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()
        cart_count = cart.total_items
        cart_total = str(cart.subtotal)
    else:
        # الضيوف
        cart = request.session.get('cart', {})
        p_id = str(product_id)
        cart[p_id] = cart.get(p_id, 0) + quantity
        request.session['cart'] = cart
        request.session.modified = True
        
        # حساب المجموع للرد
        cart_count = sum(cart.values())
        subtotal = 0
        for pid, qty in cart.items():
            p = Product.objects.filter(id=pid).first()
            if p: subtotal += p.final_price * qty
        cart_total = str(subtotal)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            "status":      "success",
            "message":     msg_success,
            "cart_count":  cart_count,
            "cart_total":  cart_total,
        })
    
    messages.success(request, msg_success)
    next_url = request.GET.get("next")
    if next_url == "checkout":
        return redirect("checkout")
    return redirect("cart")


@require_POST
def update_cart(request, item_id):
    quantity = int(request.POST.get("quantity", 1))

    if request.user.is_authenticated:
        item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        if quantity < 1:
            item.delete()
            return JsonResponse({"status": "removed"})
        if quantity > item.product.stock:
            return JsonResponse({"status": "error", "message": "الكمية تتجاوز المخزون"}, status=400)
        item.quantity = quantity
        item.save()
        cart_total = str(item.cart.subtotal)
        cart_count = item.cart.total_items
    else:
        # للضيف item_id هو الـ product_id
        cart = request.session.get('cart', {})
        p_id = str(item_id)
        if p_id in cart:
            if quantity < 1:
                del cart[p_id]
            else:
                product = get_object_or_404(Product, id=p_id)
                if quantity > product.stock:
                    return JsonResponse({"status": "error", "message": "الكمية تتجاوز المخزون"}, status=400)
                cart[p_id] = quantity
            request.session['cart'] = cart
            request.session.modified = True
        
        # حساب المجموع
        subtotal = 0
        total_items = 0
        for pid, qty in cart.items():
            p = Product.objects.filter(id=pid).first()
            if p:
                subtotal += p.final_price * qty
                total_items += qty
        cart_total = str(subtotal)
        cart_count = total_items

    return JsonResponse({
        "status":     "updated",
        "cart_total": cart_total,
        "cart_count": cart_count,
    })


@require_POST
def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        cart = item.cart
        item.delete()
        cart_count = cart.total_items
        cart_total = str(cart.subtotal)
    else:
        cart = request.session.get('cart', {})
        p_id = str(item_id)
        if p_id in cart:
            del cart[p_id]
            request.session['cart'] = cart
            request.session.modified = True
        
        # حساب المجموع
        subtotal = 0
        total_items = 0
        for pid, qty in cart.items():
            p = Product.objects.filter(id=pid).first()
            if p:
                subtotal += p.final_price * qty
                total_items += qty
        cart_total = str(subtotal)
        cart_count = total_items

    return JsonResponse({
        "status":     "removed",
        "cart_count": cart_count,
        "cart_total": cart_total,
    })






@login_required
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(customer=request.user)
    if cart.is_empty:
        return redirect("cart")

    from accounts.models import Governorate, Address, City
    from .services import apply_single_offer

    addresses    = request.user.addresses.all()
    governorates = Governorate.objects.filter(is_active=True)

    # ── حساب العروض للعرض في صفحة الـ checkout ──────────
    cart_items = []
    for item in cart.items.select_related('product'):
        cart_items.append({
            'id':         item.id,
            'product':    item.product,
            'quantity':   item.quantity,
            'unit_price': item.unit_price,
            'line_total': item.line_total,
        })

    selected_offer_id = request.session.get('selected_offer_id')
    if selected_offer_id:
        offers_result = apply_single_offer(cart_items, cart.subtotal, selected_offer_id)
    else:
        offers_result = {
            'discount_amount': 0,
            'free_items':      [],
            'free_shipping':   False,
            'applied_offers':  [],
        }

    # cart_context يجمع بيانات السلة + العروض للـ template
    cart_context = {
        'items':           cart_items,
        'subtotal':        cart.subtotal,
        'discount_amount': cart.discount_amount + offers_result['discount_amount'],
        'total':           max(cart.subtotal - cart.discount_amount - offers_result['discount_amount'], 0),
        'applied_offers':  offers_result['applied_offers'],
        'free_items':      offers_result['free_items'],
        'free_shipping':   offers_result['free_shipping'],
    }

    if request.method == "POST":
        address_id     = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method", "cod")
        notes          = request.POST.get("notes", "")

        if not address_id and request.POST.get("new_full_name"):
            try:
                new_addr = Address.objects.create(
                    customer       = request.user,
                    full_name      = request.POST.get("new_full_name"),
                    phone          = request.POST.get("new_phone"),
                    governorate_id = request.POST.get("new_governorate"),
                    city_id        = request.POST.get("new_city"),
                    street         = request.POST.get("new_street"),
                    building       = request.POST.get("new_building"),
                    is_default     = request.POST.get("save_address") == "on"
                )
                address_id = new_addr.id
            except Exception as e:
                messages.error(request, f"خطأ في إنشاء العنوان: {str(e)}")

        if not address_id:
            messages.error(request, "يرجى اختيار عنوان الشحن")
        else:
            try:
                order = create_order_from_cart(
                    customer          = request.user,
                    address_id        = address_id,
                    payment_method    = payment_method,
                    notes             = notes,
                    selected_offer_id = selected_offer_id,
                )
                # امسح العرض من السيشن بعد الطلب
                if 'selected_offer_id' in request.session:
                    del request.session['selected_offer_id']
                return redirect("order_success", order_number=order.order_number)
            except OutOfStockError as product_name:
                lang = getattr(request, 'LANGUAGE_CODE', 'ar')
                msg  = f'عذراً، المنتج "{product_name}" نفد من المخزون.' if lang != 'en' else f'Sorry, "{product_name}" is out of stock.'
                messages.error(request, msg)
                return redirect("products")
            except Exception as e:
                messages.error(request, str(e))

    return render(request, "orders/checkout.html", {
        "cart":         cart_context,
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


@require_POST
def apply_coupon(request):
    code = request.POST.get("code", "").strip()
    now  = timezone.now()
    
    try:
        coupon = Coupon.objects.get(
            code__iexact=code,
            valid_from__lte=now,
            valid_to__gte=now,
            active=True
        )
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(customer=request.user)
            cart.coupon = coupon
            cart.save()
        else:
            request.session['coupon_id'] = coupon.id
            request.session.modified = True
            
        messages.success(request, _("تم تطبيق الكوبون بنجاح") if request.LANGUAGE_CODE == 'ar' else "Coupon applied successfully")
    except Coupon.DoesNotExist:
        messages.error(request, _("كود الكوبون غير صحيح أو منتهي") if request.LANGUAGE_CODE == 'ar' else "Invalid or expired coupon code")
    
    return redirect("cart")


def track_order_view(request):
    order = None
    order_number = request.GET.get("order_number", "").strip()
    
    if order_number:
        # البحث عن الطلب برقم الطلب
        from .models import Order
        order = Order.objects.filter(order_number__iexact=order_number).first()
        if not order:
            messages.error(request, "لم يتم العثور على طلب بهذا الرقم" if request.LANGUAGE_CODE == 'ar' else "No order found with this number")
            
    return render(request, "orders/track_order.html", {
        "order": order,
        "order_number": order_number
    })


@require_POST
def remove_coupon(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(customer=request.user)
        cart.coupon = None
        cart.save()
    else:
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
            request.session.modified = True
            
    messages.success(request, _("تم إزالة الكوبون") if request.LANGUAGE_CODE == 'ar' else "Coupon removed")
    return redirect("cart")

@require_POST
def select_offer(request):
    offer_id = request.POST.get('offer_id')
    if offer_id == 'none':
        # إلغاء العرض
        if 'selected_offer_id' in request.session:
            del request.session['selected_offer_id']
    else:
        request.session['selected_offer_id'] = int(offer_id)
    request.session.modified = True
    return redirect('cart')
# apps/orders/services.py

from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Order, OrderItem
from accounts.models import Address
from .tasks import send_order_confirmation_email


class OutOfStockError(Exception):
    """يُرفع عندما يكون مخزون أحد المنتجات غير كافٍ"""
    pass


# ══════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════

def _get_active_offers():
    from .models import Offer
    now = timezone.now()
    return Offer.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_to__gte=now,
    ).prefetch_related('eligible_products', 'eligible_categories')


def _product_matches(product, offer):
    if offer.apply_to_all:
        return True
    if offer.eligible_products.filter(id=product.id).exists():
        return True
    if product.category and offer.eligible_categories.filter(id=product.category.id).exists():
        return True
    return False


# ══════════════════════════════════════════════════════════════════
# العروض المتاحة للاختيار
# ══════════════════════════════════════════════════════════════════

def get_available_offers_for_cart(cart_items, subtotal):
    """
    يرجع كل العروض المتاحة للسلة الحالية بدون تطبيق
    للعرض على العميل كـ radio buttons
    """
    available = []

    for offer in _get_active_offers():

        if offer.offer_type == offer.OfferType.BOGO:
            for item in cart_items:
                if _product_matches(item['product'], offer):
                    sets = item['quantity'] // offer.buy_quantity
                    if sets >= 1:
                        free_product = offer.free_product or item['product']
                        free_qty     = sets * offer.get_quantity
                        saving       = free_product.final_price * free_qty
                        available.append({
                            'offer':       offer,
                            'description': f"اشتري {offer.buy_quantity} وخذ {free_qty} مجاناً من {free_product.name_ar}",
                            'saving':      saving,
                        })
                        break

        elif offer.offer_type == offer.OfferType.PERCENTAGE:
            for item in cart_items:
                if _product_matches(item['product'], offer):
                    saving = sum(
                        i['line_total'] * (offer.discount_percent / 100)
                        for i in cart_items if _product_matches(i['product'], offer)
                    )
                    available.append({
                        'offer':       offer,
                        'description': f"خصم {offer.discount_percent}% — {offer.name_ar}",
                        'saving':      saving,
                    })
                    break

        elif offer.offer_type == offer.OfferType.QUANTITY:
            for item in cart_items:
                if _product_matches(item['product'], offer) and item['quantity'] >= offer.min_quantity:
                    saving = item['line_total'] * (offer.quantity_discount_percent / 100)
                    available.append({
                        'offer':       offer,
                        'description': f"خصم {offer.quantity_discount_percent}% عند شراء {offer.min_quantity}+ من {item['product'].name_ar}",
                        'saving':      saving,
                    })
                    break

        elif offer.offer_type == offer.OfferType.FREE_SHIPPING:
            check = subtotal if offer.apply_to_all else Decimal(sum(
                i['line_total'] for i in cart_items if _product_matches(i['product'], offer)
            ))
            if check >= offer.min_order_amount:
                available.append({
                    'offer':       offer,
                    'description': f"شحن مجاني — {offer.name_ar}",
                    'saving':      Decimal('0'),
                })

    return available


# ══════════════════════════════════════════════════════════════════
# تطبيق عرض واحد مختار
# ══════════════════════════════════════════════════════════════════

def apply_single_offer(cart_items, subtotal, offer_id):
    """
    يطبق عرض واحد فقط بناءً على اختيار العميل
    """
    from .models import Offer

    result = {
        'discount_amount': Decimal('0'),
        'free_items':      [],
        'free_shipping':   False,
        'applied_offers':  [],
    }

    try:
        offer = Offer.objects.prefetch_related(
            'eligible_products', 'eligible_categories'
        ).get(id=offer_id, is_active=True)
    except Offer.DoesNotExist:
        return result

    now = timezone.now()
    if not (offer.valid_from <= now <= offer.valid_to):
        return result

    if offer.offer_type == offer.OfferType.BOGO:
        for item in cart_items:
            if _product_matches(item['product'], offer):
                sets = item['quantity'] // offer.buy_quantity
                if sets >= 1:
                    free_qty     = sets * offer.get_quantity
                    free_product = offer.free_product or item['product']
                    result['free_items'].append({'product': free_product, 'quantity': free_qty})
                    result['discount_amount'] += free_product.final_price * free_qty
                    result['applied_offers'].append({
                        'offer':       offer,
                        'description': f"اشتري {offer.buy_quantity} وخذ {free_qty} مجاناً من {free_product.name_ar}",
                    })

    elif offer.offer_type == offer.OfferType.PERCENTAGE:
        added = False
        for item in cart_items:
            if _product_matches(item['product'], offer):
                result['discount_amount'] += item['line_total'] * (offer.discount_percent / 100)
                added = True
        if added:
            result['applied_offers'].append({
                'offer':       offer,
                'description': f"خصم {offer.discount_percent}% — {offer.name_ar}",
            })

    elif offer.offer_type == offer.OfferType.QUANTITY:
        for item in cart_items:
            if _product_matches(item['product'], offer) and item['quantity'] >= offer.min_quantity:
                result['discount_amount'] += item['line_total'] * (offer.quantity_discount_percent / 100)
                result['applied_offers'].append({
                    'offer':       offer,
                    'description': f"خصم {offer.quantity_discount_percent}% عند شراء {offer.min_quantity}+ من {item['product'].name_ar}",
                })

    elif offer.offer_type == offer.OfferType.FREE_SHIPPING:
        check = subtotal if offer.apply_to_all else Decimal(sum(
            i['line_total'] for i in cart_items if _product_matches(i['product'], offer)
        ))
        if check >= offer.min_order_amount:
            result['free_shipping'] = True
            result['applied_offers'].append({
                'offer':       offer,
                'description': f"شحن مجاني — {offer.name_ar}",
            })

    return result


# ══════════════════════════════════════════════════════════════════
# إنشاء الطلب
# ══════════════════════════════════════════════════════════════════

@transaction.atomic
def create_order_from_cart(customer, address_id, payment_method, notes="", selected_offer_id=None):
    cart = customer.cart

    if cart.is_empty:
        raise ValueError("السلة فارغة")

    address = Address.objects.get(id=address_id, customer=customer)

    # ── التحقق من المخزون ────────────────────────────────────────
    for item in cart.items.select_related("product"):
        if item.product.stock < item.quantity:
            raise OutOfStockError(item.product.name_ar or item.product.name_en)

    # ── بناء cart_items ──────────────────────────────────────────
    cart_items = []
    for item in cart.items.select_related("product"):
        cart_items.append({
            'id':         item.id,
            'product':    item.product,
            'quantity':   item.quantity,
            'unit_price': item.unit_price,
            'line_total': item.line_total,
        })

    subtotal = cart.subtotal

    # ── حساب الخصومات ────────────────────────────────────────────
    coupon_discount = cart.discount_amount
    coupon_code     = cart.coupon.code if cart.coupon else ""

    if selected_offer_id:
        offers_result = apply_single_offer(cart_items, subtotal, selected_offer_id)
    else:
        offers_result = {
            'discount_amount': Decimal('0'),
            'free_items':      [],
            'free_shipping':   False,
            'applied_offers':  [],
        }

    offers_discount = offers_result['discount_amount']
    total_discount  = coupon_discount + offers_discount
    shipping_cost   = Decimal('0') if offers_result['free_shipping'] else address.city.shipping_cost
    total           = max(subtotal + shipping_cost - total_discount, Decimal('0'))

    # ── إنشاء الطلب ──────────────────────────────────────────────
    order = Order.objects.create(
        customer             = customer,
        shipping_full_name   = address.full_name,
        shipping_phone       = address.phone,
        shipping_governorate = address.governorate.name_ar,
        shipping_city        = address.city.name_ar,
        shipping_street      = address.street,
        shipping_building    = address.building,
        subtotal             = subtotal,
        shipping_cost        = shipping_cost,
        discount_amount      = total_discount,
        total                = total,
        payment_method       = payment_method,
        coupon_code          = coupon_code,
        notes                = notes,
    )

    # ── نسخ عناصر السلة للطلب ────────────────────────────────────
    for item in cart.items.select_related("product"):
        OrderItem.objects.create(
            order         = order,
            product       = item.product,
            product_name  = item.product.name_ar,
            product_sku   = item.product.sku,
            product_image = item.product.thumbnail.url if item.product.thumbnail else "",
            unit_price    = item.unit_price,
            quantity      = item.quantity,
        )
        item.product.stock -= item.quantity
        item.product.save(update_fields=["stock"])

    # ── تفريغ السلة ──────────────────────────────────────────────
    cart.items.all().delete()
    cart.coupon = None
    cart.save()

    return order
# apps/orders/services.py  —  منطق إنشاء الطلب

from django.db import transaction
from .models import Order, OrderItem
from accounts.models import Address


@transaction.atomic
def create_order_from_cart(customer, address_id, payment_method, notes="", coupon=None):
    """
    تحوّل محتوى السلة لطلب حقيقي في خطوة واحدة atomic
    """
    cart = customer.cart

    if cart.is_empty:
        raise ValueError("السلة فارغة")

    address = Address.objects.get(id=address_id, customer=customer)

    # ── حساب الخصم ───────────────────────────────────────────────
    discount_amount = 0
    coupon_code     = ""
    if coupon:
        discount_amount = coupon.calc_discount(cart.subtotal)
        coupon_code     = coupon.code

    shipping_cost = address.city.shipping_cost
    subtotal      = cart.subtotal
    total         = subtotal + shipping_cost - discount_amount

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
        discount_amount      = discount_amount,
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
        # ── تخفيض المخزون ────────────────────────────────────────
        item.product.stock -= item.quantity
        item.product.save(update_fields=["stock"])

    # ── تفريغ السلة بعد الطلب ────────────────────────────────────
    cart.items.all().delete()

    return order
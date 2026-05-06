# core/dashboard.py  —  منطق الإحصاءات

from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from products.models import Product
from accounts.models import Customer
from reviews.models import Review


def get_dashboard_stats():
    now   = timezone.now()
    today = now.date()
    month_start = now.replace(day=1, hour=0, minute=0, second=0)
    last_30     = now - timedelta(days=30)

    # ── الإحصاءات الرئيسية ────────────────────────────────────────
    total_revenue   = Order.objects.filter(
        status=Order.Status.DELIVERED
    ).aggregate(total=Sum("total"))["total"] or 0

    month_revenue   = Order.objects.filter(
        status=Order.Status.DELIVERED,
        created_at__gte=month_start,
    ).aggregate(total=Sum("total"))["total"] or 0

    today_orders    = Order.objects.filter(created_at__date=today).count()
    pending_orders  = Order.objects.filter(status=Order.Status.PENDING).count()
    total_customers = Customer.objects.filter(is_active=True).count()
    new_customers   = Customer.objects.filter(created_at__gte=last_30).count()
    total_products  = Product.objects.filter(is_active=True).count()
    out_of_stock    = Product.objects.filter(is_active=True, stock=0).count()
    low_stock       = Product.objects.filter(is_active=True, stock__gt=0, stock__lte=5).count()

    # ── مبيعات آخر 7 أيام ────────────────────────────────────────
    last_7 = now - timedelta(days=7)
    sales_chart = (
        Order.objects
        .filter(created_at__gte=last_7)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"), revenue=Sum("total"))
        .order_by("day")
    )

    # ── أحدث 10 طلبات ─────────────────────────────────────────────
    recent_orders = (
        Order.objects
        .select_related("customer")
        .order_by("-created_at")[:10]
    )

    # ── أكثر المنتجات مبيعاً ──────────────────────────────────────
    top_products = (
        Product.objects
        .annotate(sold=Sum("order_items__quantity"))
        .filter(sold__isnull=False)
        .order_by("-sold")[:5]
    )

    # ── توزيع الطلبات حسب الحالة ──────────────────────────────────
    orders_by_status = (
        Order.objects
        .values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    return {
        "total_revenue":   total_revenue,
        "month_revenue":   month_revenue,
        "today_orders":    today_orders,
        "pending_orders":  pending_orders,
        "total_customers": total_customers,
        "new_customers":   new_customers,
        "total_products":  total_products,
        "out_of_stock":    out_of_stock,
        "low_stock":       low_stock,
        "sales_chart":     list(sales_chart),
        "recent_orders":   recent_orders,
        "top_products":    top_products,
        "orders_by_status": list(orders_by_status),
    }
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Coupon(models.Model):
    code       = models.CharField(max_length=50, unique=True, verbose_name="كود الكوبون")
    valid_from = models.DateTimeField(verbose_name="صالح من")
    valid_to   = models.DateTimeField(verbose_name="صالح إلى")
    discount   = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="نسبة الخصم (%)"
    )
    active     = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        verbose_name        = "كوبون"
        verbose_name_plural = "الكوبونات"

    def __str__(self):
        return self.code


class Cart(models.Model):
    customer   = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="العميل",
    )
    coupon     = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="carts",
        verbose_name="الكوبون",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "سلة تسوق"
        verbose_name_plural = "سلال التسوق"

    def __str__(self):
        return f"سلة {self.customer.get_full_name()}"

    # ── Properties ───────────────────────────────────────────────
    @property
    def total_items(self):
        """إجمالي عدد القطع في السلة"""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """المجموع قبل الشحن والخصم"""
        return sum(item.line_total for item in self.items.all())

    @property
    def discount_amount(self):
        if self.coupon:
            return (self.subtotal * self.coupon.discount) / 100
        return 0

    @property
    def total(self):
        """المجموع بعد الخصم"""
        return self.subtotal - self.discount_amount

    @property
    def is_empty(self):
        return not self.items.exists()


class CartItem(models.Model):
    cart     = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="السلة",
    )
    product  = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="المنتج",
    )
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name="الكمية")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "عنصر في السلة"
        verbose_name_plural = "عناصر السلة"
        unique_together     = ("cart", "product")   # منتج واحد مرة واحدة في السلة

    def __str__(self):
        return f"{self.product.name_ar} × {self.quantity}"

    @property
    def unit_price(self):
        """سعر الوحدة (يأخذ الخصم لو موجود)"""
        return self.product.final_price

    @property
    def line_total(self):
        """سعر السطر = الكمية × سعر الوحدة"""
        return (self.unit_price or 0) * (self.quantity or 0)
    


class Order(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    # ── حالات الطلب ──────────────────────────────────────────────
    class Status(models.TextChoices):
        PENDING    = "pending",    "قيد الانتظار"
        PROCESSING = "processing", "قيد المعالجة"
        SHIPPED    = "shipped",    "تم الشحن"
        DELIVERED  = "delivered",  "تم التسليم"
        CANCELLED  = "cancelled",  "ملغي"
        REFUNDED   = "refunded",   "مُسترد"

    # ── طرق الدفع ────────────────────────────────────────────────
    class PaymentMethod(models.TextChoices):
        COD    = "cod",    "الدفع عند الاستلام"
        CARD   = "card",   "بطاقة إلكترونية"
        WALLET = "wallet", "محفظة إلكترونية"

    # ── بيانات الطلب ─────────────────────────────────────────────
    order_number   = models.CharField(max_length=20, unique=True, blank=True, verbose_name="رقم الطلب")
    customer       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="orders",
        verbose_name="العميل",
    )

    # ── بيانات الشحن (snapshot وقت الطلب) ────────────────────────
    shipping_full_name   = models.CharField(max_length=100, verbose_name="اسم المستلم")
    shipping_phone       = models.CharField(max_length=20,  verbose_name="هاتف المستلم")
    shipping_governorate = models.CharField(max_length=100, verbose_name="المحافظة")
    shipping_city        = models.CharField(max_length=100, verbose_name="المدينة")
    shipping_street      = models.CharField(max_length=255, verbose_name="الشارع")
    shipping_building    = models.CharField(max_length=50, blank=True, verbose_name="المبنى / الشقة")

    # ── المبالغ ───────────────────────────────────────────────────
    subtotal        = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المجموع الجزئي")
    shipping_cost   = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="تكلفة الشحن")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="قيمة الخصم")
    total           = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الإجمالي")

    # ── الدفع ────────────────────────────────────────────────────
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
        verbose_name="طريقة الدفع",
    )
    is_paid    = models.BooleanField(default=False, verbose_name="تم الدفع")
    paid_at    = models.DateTimeField(null=True, blank=True, verbose_name="وقت الدفع")

    # ── الحالة ───────────────────────────────────────────────────
    status     = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="حالة الطلب",
    )

    # ── الكوبون ──────────────────────────────────────────────────
    coupon_code = models.CharField(max_length=50, blank=True, verbose_name="كود الخصم")

    # ── ملاحظات ──────────────────────────────────────────────────
    notes      = models.TextField(blank=True, verbose_name="ملاحظات العميل")

    # ── التواريخ ─────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "طلب"
        verbose_name_plural = "الطلبات"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"طلب #{self.order_number} — {self.customer}"

    # ── توليد رقم الطلب تلقائياً ─────────────────────────────────
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        return "ORD-" + uuid.uuid4().hex[:8].upper()   # مثال: ORD-A3F9C21B

    # ── Properties ───────────────────────────────────────────────
    @property
    def status_badge_color(self):
        colors = {
            "pending":    "#f39c12",
            "processing": "#3498db",
            "shipped":    "#9b59b6",
            "delivered":  "#27ae60",
            "cancelled":  "#e74c3c",
            "refunded":   "#95a5a6",
        }
        return colors.get(self.status, "#999")

    @property
    def can_cancel(self):
        """العميل يقدر يلغي لو لسه pending أو processing"""
        return self.status in [self.Status.PENDING, self.Status.PROCESSING]

    @property
    def shipping_address_display(self):
        parts = [self.shipping_governorate, self.shipping_city, self.shipping_street]
        if self.shipping_building:
            parts.append(self.shipping_building)
        return " — ".join(parts)


class OrderItem(models.Model):
    order    = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="الطلب",
    )

    # ── snapshot من المنتج وقت الشراء ────────────────────────────
    product       = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
        verbose_name="المنتج",
    )
    product_name  = models.CharField(max_length=255, verbose_name="اسم المنتج")   # snapshot
    product_sku   = models.CharField(max_length=20,  verbose_name="كود المنتج")   # snapshot
    product_image = models.CharField(max_length=500, blank=True, verbose_name="صورة المنتج")  # snapshot

    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    quantity   = models.PositiveSmallIntegerField(default=1, verbose_name="الكمية")

    class Meta:
        verbose_name        = "عنصر في الطلب"
        verbose_name_plural = "عناصر الطلبات"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def line_total(self):
        return (self.unit_price or 0) * (self.quantity or 0)


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    if not created and instance.status != getattr(instance, '_original_status', None):
        # Update original status to avoid double triggers if saved again in same request
        # Update original status to avoid double triggers if saved again in same request
        instance._original_status = instance.status
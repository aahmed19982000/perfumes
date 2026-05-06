# apps/reviews/models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):

    # ── التقييم بالنجوم ──────────────────────────────────────────
    class Rating(models.IntegerChoices):
        ONE   = 1, "⭐ ضعيف"
        TWO   = 2, "⭐⭐ مقبول"
        THREE = 3, "⭐⭐⭐ جيد"
        FOUR  = 4, "⭐⭐⭐⭐ جيد جداً"
        FIVE  = 5, "⭐⭐⭐⭐⭐ ممتاز"

    # ── العلاقات ─────────────────────────────────────────────────
    product  = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="المنتج",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="العميل",
    )

    # ── المحتوى ──────────────────────────────────────────────────
    rating  = models.PositiveSmallIntegerField(
        choices=Rating.choices,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="التقييم",
    )
    title   = models.CharField(max_length=100, blank=True, verbose_name="عنوان التقييم")
    comment = models.TextField(blank=True, verbose_name="التعليق")

    # ── الإشراف ──────────────────────────────────────────────────
    is_approved = models.BooleanField(default=True, verbose_name="معتمد")

    # ── التواريخ ─────────────────────────────────────────────────
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "تقييم"
        verbose_name_plural = "التقييمات"
        ordering            = ["-created_at"]
        unique_together     = ("product", "customer")   # تقييم واحد لكل منتج لكل عميل

    def __str__(self):
        return f"{self.customer.get_full_name()} — {self.product.name_ar} ({self.rating}★)"

    # ── Properties ───────────────────────────────────────────────
    @property
    def stars_range(self):
        """للـ template: range(1,6) عشان نرسم النجوم"""
        return range(1, 6)

    @property
    def can_edit(self):
        """العميل يقدر يعدّل خلال 48 ساعة"""
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        return delta.total_seconds() < 48 * 3600


class ReviewSummary(models.Model):
    """
    جدول مخصص يخزّن إحصاءات التقييم لكل منتج
    بيتحدّث تلقائياً عن طريق signals — أسرع من COUNT/AVG في كل request
    """
    product       = models.OneToOneField(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="review_summary",
        verbose_name="المنتج",
    )
    avg_rating    = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    count_1_star  = models.PositiveIntegerField(default=0)
    count_2_star  = models.PositiveIntegerField(default=0)
    count_3_star  = models.PositiveIntegerField(default=0)
    count_4_star  = models.PositiveIntegerField(default=0)
    count_5_star  = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "ملخص تقييمات"

    def __str__(self):
        return f"{self.product.name_ar} — {self.avg_rating}★ ({self.total_reviews})"

    @property
    def rating_percent(self):
        """نسبة كل تقييم للـ progress bar"""
        total = self.total_reviews or 1
        return {
            star: round(getattr(self, f"count_{star}_star") / total * 100)
            for star in range(1, 6)
        }
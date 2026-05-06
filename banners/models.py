# banners/models.py

from django.db import models


class Banner(models.Model):

    # ── نوع البانر ───────────────────────────────────────────────
    class Position(models.TextChoices):
        HERO       = "hero",       "السلايدر الرئيسي"
        SECONDARY  = "secondary",  "بانر ثانوي"
        POPUP      = "popup",      "نافذة منبثقة"

    # ── البيانات ─────────────────────────────────────────────────
    title_ar   = models.CharField(max_length=200, blank=True, verbose_name="العنوان بالعربي")
    title_en   = models.CharField(max_length=200, blank=True, verbose_name="العنوان بالإنجليزي")
    image      = models.ImageField(upload_to="banner/", verbose_name="الصورة")
    link       = models.URLField(blank=True, verbose_name="الرابط عند الضغط")
    position   = models.CharField(
        max_length=15,
        choices=Position.choices,
        default=Position.HERO,
        verbose_name="الموضع",
    )
    order      = models.PositiveSmallIntegerField(default=0, verbose_name="الترتيب")
    is_active  = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "بانر"
        verbose_name_plural = "البانرات"
        ordering            = ["order", "-created_at"]

    def __str__(self):
        return f"{self.get_position_display()} — {self.title_ar or self.title_en or 'بدون عنوان'}"
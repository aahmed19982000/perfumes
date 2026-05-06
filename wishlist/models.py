# apps/wishlist/models.py

from django.db import models
from django.conf import settings


class Wishlist(models.Model):
    customer   = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name="العميل",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "قائمة أمنيات"
        verbose_name_plural = "قوائم الأمنيات"

    def __str__(self):
        return f"أمنيات {self.customer.get_full_name()}"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def is_empty(self):
        return not self.items.exists()


class WishlistItem(models.Model):
    wishlist   = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="قائمة الأمنيات",
    )
    product    = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name="المنتج",
    )
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "عنصر في الأمنيات"
        verbose_name_plural = "عناصر الأمنيات"
        unique_together     = ("wishlist", "product")   # منتج واحد مرة واحدة
        ordering            = ["-added_at"]

    def __str__(self):
        return f"{self.product.name_ar} — {self.wishlist.customer.get_full_name()}"
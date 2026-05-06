# apps/products/models.py

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name="الاسم بالعربي")
    name_en = models.CharField(max_length=100, verbose_name="الاسم بالإنجليزي")
    slug    = models.SlugField(unique=True, blank=True)
    image   = models.ImageField(upload_to="category/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "فئة"
        verbose_name_plural = "الفئات"
        ordering = ["name_ar"]

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="sub_categories",
        verbose_name="الفئة الرئيسية",
    )
    name_ar = models.CharField(max_length=100, verbose_name="الاسم بالعربي")
    name_en = models.CharField(max_length=100, verbose_name="الاسم بالإنجليزي")
    slug    = models.SlugField(unique=True, blank=True)
    image   = models.ImageField(upload_to="sub_category/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "فئة فرعية"
        verbose_name_plural = "الفئات الفرعية"
        ordering = ["name_ar"]

    def __str__(self):
        return f"{self.category.name_ar} ← {self.name_ar}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)








class Brand(models.Model):
    name       = models.CharField(max_length=100, verbose_name="اسم العلامة التجارية")
    slug       = models.SlugField(unique=True, blank=True)
    logo       = models.ImageField(upload_to="brand/", blank=True, null=True, verbose_name="الشعار")
    is_active  = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "علامة تجارية"
        verbose_name_plural = "العلامات التجارية"
        ordering            = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def product_count(self):
        return self.products.count()
    




# apps/products/models.py  —  أضف بعد Brand

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Product(models.Model):
    # ── المعرّف الفريد ──────────────────────────────────────────
    sku  = models.CharField(max_length=20, unique=True, blank=True, verbose_name="كود المنتج")

    # ── الأسماء والوصف ─────────────────────────────────────────
    name_ar        = models.CharField(max_length=255, verbose_name="الاسم بالعربي")
    name_en        = models.CharField(max_length=255, verbose_name="الاسم بالإنجليزي")
    slug           = models.SlugField(unique=True, blank=True, max_length=300)
    description_ar = models.TextField(blank=True, verbose_name="الوصف بالعربي")
    description_en = models.TextField(blank=True, verbose_name="الوصف بالإنجليزي")

    # ── العلاقات ────────────────────────────────────────────────
    category     = models.ForeignKey(
        "Category", on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products", verbose_name="الفئة",
    )
    sub_category = models.ForeignKey(
        "SubCategory", on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products", verbose_name="الفئة الفرعية",
    )
    brand = models.ForeignKey(
        "Brand", on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products", verbose_name="العلامة التجارية",
    )

    # ── السعر والمخزون ──────────────────────────────────────────
    price          = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name="سعر بعد الخصم",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="المخزون")

    # ── الصورة الرئيسية ─────────────────────────────────────────
    thumbnail = models.ImageField(
        upload_to="product/thumbnail/",
        verbose_name="الصورة الرئيسية",
    )

    # ── الحالة والتصنيف ─────────────────────────────────────────
    is_active   = models.BooleanField(default=True,  verbose_name="نشط")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")

    # ── التواريخ ────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "منتج"
        verbose_name_plural = "المنتجات"
        ordering            = ["-created_at"]

    def __str__(self):
        return self.name_ar

    # ── توليد SKU و Slug تلقائياً ────────────────────────────────
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = uuid.uuid4().hex[:8].upper()   # مثال: A3F9C21B
        if not self.slug:
            base = slugify(self.name_en) or slugify(self.name_ar)
            self.slug = f"{base}-{self.sku}"
        super().save(*args, **kwargs)

    # ── Properties مساعدة ────────────────────────────────────────
    @property
    def is_out_of_stock(self):
        return self.stock == 0

    @property
    def final_price(self):
        """السعر الفعلي بعد الخصم إن وجد"""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        """نسبة الخصم"""
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def review_count(self):
        return self.reviews.count()


class ProductImage(models.Model):
    product   = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="images", verbose_name="المنتج",
    )
    image     = models.ImageField(upload_to="product/images/", verbose_name="الصورة")
    alt_text  = models.CharField(max_length=150, blank=True, verbose_name="النص البديل")
    is_main   = models.BooleanField(default=False, verbose_name="صورة رئيسية")
    order     = models.PositiveSmallIntegerField(default=0, verbose_name="الترتيب")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "صورة منتج"
        verbose_name_plural = "صور المنتجات"
        ordering            = ["order", "created_at"]

    def __str__(self):
        return f"صورة — {self.product.name_ar}"
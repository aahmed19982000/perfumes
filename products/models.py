# products/models.py

from django.db import models
from django.utils.text import slugify
from PIL import Image
import uuid
import os

def generate_unique_slug(instance, base_str, slug_field_name='slug'):
    base_slug = slugify(base_str, allow_unicode=True) if base_str else ''
    if not base_slug:
        base_slug = str(uuid.uuid4())[:8]
    
    slug = base_slug
    ModelClass = instance.__class__
    counter = 1
    while ModelClass.objects.filter(**{slug_field_name: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


# ══════════════════════════════════════════════════════════════════
# UTILS
# ══════════════════════════════════════════════════════════════════

def compress_image(image_field, max_width=1200, quality=82):
    """
    ضغط الصورة وتحويلها لـ WebP
    quality=82 = أفضل نقطة توازن بين الجودة والحجم
    method=6   = أعلى جودة ضغط (أبطأ في الحفظ لكن أصغر حجم)
    """
    img = Image.open(image_field.path)

    # تحويل RGBA أو P لـ RGB عشان WebP
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # تصغير الأبعاد فقط لو الصورة أكبر من max_width
    if img.width > max_width:
        ratio      = max_width / img.width
        new_height = int(img.height * ratio)
        img        = img.resize((max_width, new_height), Image.LANCZOS)

    old_path  = image_field.path
    webp_path = os.path.splitext(old_path)[0] + ".webp"

    img.save(
        webp_path,
        format="WEBP",
        quality=quality,
        optimize=True,
        method=6,
        lossless=False,
    )

    # حذف الصورة الأصلية لو اختلف الامتداد
    if old_path != webp_path and os.path.exists(old_path):
        os.remove(old_path)

    return os.path.basename(webp_path)


# ══════════════════════════════════════════════════════════════════
# CATEGORY
# ══════════════════════════════════════════════════════════════════

class Category(models.Model):
    name_ar    = models.CharField(max_length=100, verbose_name="الاسم بالعربي")
    name_en    = models.CharField(max_length=100, verbose_name="الاسم بالإنجليزي")
    slug       = models.SlugField(unique=True, blank=True, allow_unicode=True)
    image      = models.ImageField(upload_to="category/", blank=True, null=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "فئة"
        verbose_name_plural = "الفئات"
        ordering            = ["name_ar"]

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name_en or self.name_ar)
        super().save(*args, **kwargs)

        if self.image:
            try:
                # 500px كافية للفئات — بتظهر كأيقونات صغيرة
                new_name     = compress_image(self.image, max_width=500, quality=82)
                new_relative = os.path.join("category", new_name)
                if self.image.name != new_relative:
                    Category.objects.filter(pk=self.pk).update(image=new_relative)
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════
# SUBCATEGORY
# ══════════════════════════════════════════════════════════════════

class SubCategory(models.Model):
    category   = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="sub_categories",
        verbose_name="الفئة الرئيسية",
    )
    name_ar    = models.CharField(max_length=100, verbose_name="الاسم بالعربي")
    name_en    = models.CharField(max_length=100, verbose_name="الاسم بالإنجليزي")
    slug       = models.SlugField(unique=True, blank=True, allow_unicode=True)
    image      = models.ImageField(upload_to="sub_category/", blank=True, null=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "فئة فرعية"
        verbose_name_plural = "الفئات الفرعية"
        ordering            = ["name_ar"]

    def __str__(self):
        return f"{self.category.name_ar} ← {self.name_ar}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name_en or self.name_ar)
        super().save(*args, **kwargs)

        if self.image:
            try:
                # 500px كافية للفئات الفرعية
                new_name     = compress_image(self.image, max_width=500, quality=82)
                new_relative = os.path.join("sub_category", new_name)
                if self.image.name != new_relative:
                    SubCategory.objects.filter(pk=self.pk).update(image=new_relative)
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════
# BRAND
# ══════════════════════════════════════════════════════════════════

class Brand(models.Model):
    name       = models.CharField(max_length=100, verbose_name="اسم العلامة التجارية")
    slug       = models.SlugField(unique=True, blank=True, allow_unicode=True)
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
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

        if self.logo:
            try:
                # 300px كافية للشعارات — بتظهر صغيرة في صف البراندات
                # quality=88 عشان الشعارات فيها نص وتفاصيل دقيقة
                new_name     = compress_image(self.logo, max_width=300, quality=88)
                new_relative = os.path.join("brand", new_name)
                if self.logo.name != new_relative:
                    Brand.objects.filter(pk=self.pk).update(logo=new_relative)
            except Exception:
                pass

    def product_count(self):
        return self.products.count()


# ══════════════════════════════════════════════════════════════════
# PRODUCT
# ══════════════════════════════════════════════════════════════════

class Product(models.Model):

    # ── المعرّف الفريد ────────────────────────────────────────────
    sku  = models.CharField(max_length=20, unique=True, blank=True, verbose_name="كود المنتج")

    # ── الأسماء والوصف ───────────────────────────────────────────
    name_ar        = models.CharField(max_length=255, verbose_name="الاسم بالعربي")
    name_en        = models.CharField(max_length=255, verbose_name="الاسم بالإنجليزي")
    slug           = models.SlugField(unique=True, blank=True, max_length=300, allow_unicode=True)
    description_ar = models.TextField(blank=True, verbose_name="الوصف بالعربي")
    description_en = models.TextField(blank=True, verbose_name="الوصف بالإنجليزي")
    size           = models.CharField(max_length=50, blank=True, null=True, verbose_name="الحجم")

    # ── العلاقات ─────────────────────────────────────────────────
    category = models.ForeignKey(
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

    # ── السعر والمخزون ───────────────────────────────────────────
    price          = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name="سعر بعد الخصم",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="المخزون")

    # ── الصورة الرئيسية ──────────────────────────────────────────
    thumbnail = models.ImageField(
        upload_to="product/thumbnail/",
        verbose_name="الصورة الرئيسية",
    )

    # ── الحالة والتصنيف ──────────────────────────────────────────
    is_active   = models.BooleanField(default=True,  verbose_name="نشط")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")

    # ── التواريخ ─────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "منتج"
        verbose_name_plural = "المنتجات"
        ordering            = ["-created_at"]

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = uuid.uuid4().hex[:8].upper()
        if not self.slug:
            base      = slugify(self.name_en) or slugify(self.name_ar)
            self.slug = f"{base}-{self.sku}"

        super().save(*args, **kwargs)

        if self.thumbnail:
            try:
                # 600px كافية للـ thumbnail — بيظهر في بطاقة المنتج
                # مش محتاج أكبر لأنه مش الصورة الرئيسية في صفحة المنتج
                new_name     = compress_image(self.thumbnail, max_width=600, quality=82)
                new_relative = os.path.join("product/thumbnail", new_name)
                if self.thumbnail.name != new_relative:
                    Product.objects.filter(pk=self.pk).update(thumbnail=new_relative)
            except Exception:
                pass

    # ── Properties ───────────────────────────────────────────────
    @property
    def is_out_of_stock(self):
        return self.stock == 0

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
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


# ══════════════════════════════════════════════════════════════════
# PRODUCT IMAGE
# ══════════════════════════════════════════════════════════════════

class ProductImage(models.Model):
    product    = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="images", verbose_name="المنتج",
    )
    image      = models.ImageField(upload_to="product/images/", verbose_name="الصورة")
    alt_text   = models.CharField(max_length=150, blank=True, verbose_name="النص البديل")
    is_main    = models.BooleanField(default=False, verbose_name="صورة رئيسية")
    order      = models.PositiveSmallIntegerField(default=0, verbose_name="الترتيب")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "صورة منتج"
        verbose_name_plural = "صور المنتجات"
        ordering            = ["order", "created_at"]

    def __str__(self):
        return f"صورة — {self.product.name_ar}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            try:
                # 1000px للصور الكبيرة في معرض المنتج
                # quality=82 sweet spot للعطور (صور زجاجات واضحة)
                new_name     = compress_image(self.image, max_width=1000, quality=82)
                new_relative = os.path.join("product/images", new_name)
                if self.image.name != new_relative:
                    ProductImage.objects.filter(pk=self.pk).update(image=new_relative)
            except Exception:
                pass
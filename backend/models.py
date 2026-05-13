from django.db import models


class HeaderSettings(models.Model):
    phone_number = models.CharField("رقم الهاتف", max_length=30, default="+201069545469")
    logo_text = models.CharField("نص اللوجو", max_length=30, default="MAV")
    logo_accent = models.CharField("الحرف المميز في اللوجو", max_length=5, default="A")

    show_top_bar = models.BooleanField("إظهار الشريط العلوي", default=True)
    show_phone = models.BooleanField("إظهار رقم الهاتف", default=True)
    show_language_switcher = models.BooleanField("إظهار اختيار اللغة", default=True)
    show_search = models.BooleanField("إظهار البحث", default=True)
    show_wishlist = models.BooleanField("إظهار المفضلة", default=True)
    show_cart = models.BooleanField("إظهار السلة", default=True)

    search_placeholder_ar = models.CharField("نص البحث بالعربي", max_length=100, default="ابحث عن العطر...")
    search_placeholder_en = models.CharField("نص البحث بالإنجليزي", max_length=100, default="Search perfumes...")
    mobile_search_placeholder_ar = models.CharField("نص بحث الموبايل بالعربي", max_length=100, default="ابحث...")
    mobile_search_placeholder_en = models.CharField("نص بحث الموبايل بالإنجليزي", max_length=100, default="Search...")

    show_home_link = models.BooleanField("إظهار الرئيسية", default=True)
    home_label_ar = models.CharField("عنوان الرئيسية بالعربي", max_length=50, default="الرئيسية")
    home_label_en = models.CharField("عنوان الرئيسية بالإنجليزي", max_length=50, default="Home")

    show_categories_link = models.BooleanField("إظهار الفئات", default=True)
    categories_label_ar = models.CharField("عنوان الفئات بالعربي", max_length=50, default="الفئات")
    categories_label_en = models.CharField("عنوان الفئات بالإنجليزي", max_length=50, default="Categories")
    categories_menu_title_ar = models.CharField("عنوان قائمة الفئات بالعربي", max_length=80, default="تصفح حسب الفئة")
    categories_menu_title_en = models.CharField("عنوان قائمة الفئات بالإنجليزي", max_length=80, default="Browse by Category")

    show_offers_link = models.BooleanField("إظهار العروض", default=True)
    offers_label_ar = models.CharField("عنوان العروض بالعربي", max_length=50, default="العروض")
    offers_label_en = models.CharField("عنوان العروض بالإنجليزي", max_length=50, default="Offers")

    show_brands_link = models.BooleanField("إظهار الماركات", default=True)
    brands_label_ar = models.CharField("عنوان الماركات بالعربي", max_length=50, default="الماركات")
    brands_label_en = models.CharField("عنوان الماركات بالإنجليزي", max_length=50, default="Brands")

    show_track_order_link = models.BooleanField("إظهار تتبع الطلب", default=True)
    track_order_label_ar = models.CharField("عنوان تتبع الطلب بالعربي", max_length=50, default="تتبع الطلب")
    track_order_label_en = models.CharField("عنوان تتبع الطلب بالإنجليزي", max_length=50, default="Track Order")

    show_about_link = models.BooleanField("إظهار من نحن", default=True)
    about_label_ar = models.CharField("عنوان من نحن بالعربي", max_length=50, default="من نحن")
    about_label_en = models.CharField("عنوان من نحن بالإنجليزي", max_length=50, default="About")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إعدادات الهيدر"
        verbose_name_plural = "إعدادات الهيدر"

    def __str__(self):
        return "إعدادات الهيدر"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

from django.db import models


class HeaderSettings(models.Model):
    phone_number = models.CharField("رقم الهاتف", max_length=30, default="+201069545469")
    logo_text = models.CharField("نص اللوجو", max_length=30, default="MAV")
    logo_accent = models.CharField("الحرف المميز في اللوجو", max_length=5, default="A")
    logo_image = models.ImageField("صورة اللوجو", upload_to="settings/", null=True, blank=True)
    favicon = models.ImageField("الأيقونة (Favicon)", upload_to="settings/", null=True, blank=True)

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


class FooterSettings(models.Model):
    logo_text = models.CharField("نص اللوجو (الفوتر)", max_length=30, default="MAV")
    logo_accent = models.CharField("الحرف المميز (الفوتر)", max_length=5, default="A")
    logo_image = models.ImageField("صورة اللوجو (الفوتر)", upload_to="settings/", null=True, blank=True)

    tagline_ar = models.CharField("النص التعريفي القصير بالعربي", max_length=100, default="عطور فاخرة — منذ ٢٠٢٠")
    tagline_en = models.CharField("النص التعريفي القصير بالإنجليزي", max_length=100, default="Luxury Perfumes — Est. 2020")

    about_text_ar = models.TextField("عن المتجر بالعربي", default="اكتشف مجموعتنا المختارة من العطور الفاخرة من حول العالم.")
    about_text_en = models.TextField("عن المتجر بالإنجليزي", default="Discover our curated collection of luxury fragrances from around the world.")

    # Social links
    fb_link = models.URLField("رابط فيسبوك", blank=True, null=True)
    insta_link = models.URLField("رابط إنستجرام", blank=True, null=True)
    wa_link = models.CharField("رابط/رقم واتساب", max_length=100, default="201069545469")
    tiktok_link = models.URLField("رابط تيك توك", blank=True, null=True)

    # Contact
    phone = models.CharField("رقم الهاتف", max_length=30, default="+201069545469")
    email = models.EmailField("البريد الإلكتروني", default="info@mavaperfumes.com")
    working_hours_ar = models.CharField("ساعات العمل بالعربي", max_length=100, default="السبت – الخميس: ١٠ص – ١٠م")
    working_hours_en = models.CharField("ساعات العمل بالإنجليزي", max_length=100, default="Sat – Thu: 10am – 10pm")
    address_ar = models.CharField("العنوان بالعربي", max_length=200, default="مصر")
    address_en = models.CharField("العنوان بالإنجليزي", max_length=200, default="Egypt")

    # Copyright
    copyright_text_ar = models.CharField("نص حقوق النشر بالعربي", max_length=200, default="© 2025 مافا للعطور. جميع الحقوق محفوظة.")
    copyright_text_en = models.CharField("نص حقوق النشر بالإنجليزي", max_length=200, default="© 2025 MAVA Perfumes. All rights reserved.")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إعدادات الفوتر"
        verbose_name_plural = "إعدادات الفوتر"

    def __str__(self):
        return "إعدادات الفوتر"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

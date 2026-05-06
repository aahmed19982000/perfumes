# apps/accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("الإيميل مطلوب")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class Customer(AbstractBaseUser, PermissionsMixin):
    email      = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    first_name = models.CharField(max_length=50, verbose_name="الاسم الأول")
    last_name  = models.CharField(max_length=50, verbose_name="الاسم الأخير")
    phone      = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    avatar     = models.ImageField(upload_to="customer/avatars/", blank=True, null=True, verbose_name="الصورة الشخصية")
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects  = CustomerManager()

    USERNAME_FIELD  = "email"          # تسجيل الدخول بالإيميل مش username
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name        = "عميل"
        verbose_name_plural = "العملاء"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_default_address(self):
        return self.addresses.filter(is_default=True).first()


class Address(models.Model):
    GOVERNORATES = [
        ("cairo",          "القاهرة"),
        ("giza",           "الجيزة"),
        ("alexandria",     "الإسكندرية"),
        ("luxor",          "الأقصر"),
        ("aswan",          "أسوان"),
        ("port_said",      "بورسعيد"),
        ("suez",           "السويس"),
        ("mansoura",       "المنصورة"),
        ("tanta",          "طنطا"),
        ("zagazig",        "الزقازيق"),
        ("ismailia",       "الإسماعيلية"),
        ("fayoum",         "الفيوم"),
        ("minya",          "المنيا"),
        ("asyut",          "أسيوط"),
        ("sohag",          "سوهاج"),
        ("qena",           "قنا"),
        ("beni_suef",      "بني سويف"),
        ("dakahlia",       "الدقهلية"),
        ("sharqia",        "الشرقية"),
        ("gharbia",        "الغربية"),
        ("kafr_el_sheikh", "كفر الشيخ"),
        ("beheira",        "البحيرة"),
        ("monufia",        "المنوفية"),
        ("qalyubia",       "القليوبية"),
        ("damietta",       "دمياط"),
        ("north_sinai",    "شمال سيناء"),
        ("south_sinai",    "جنوب سيناء"),
        ("red_sea",        "البحر الأحمر"),
        ("matrouh",        "مطروح"),
        ("new_valley",     "الوادي الجديد"),
    ]

    customer     = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses", verbose_name="العميل")
    full_name    = models.CharField(max_length=100, verbose_name="الاسم الكامل")
    phone        = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    governorate  = models.CharField(max_length=50, choices=GOVERNORATES, verbose_name="المحافظة")
    city         = models.CharField(max_length=100, verbose_name="المدينة / الحي")
    street       = models.CharField(max_length=255, verbose_name="الشارع")
    building     = models.CharField(max_length=50, blank=True, verbose_name="رقم المبنى / الشقة")
    postal_code  = models.CharField(max_length=10, blank=True, verbose_name="الرمز البريدي")
    is_default   = models.BooleanField(default=False, verbose_name="العنوان الافتراضي")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "عنوان"
        verbose_name_plural = "العناوين"
        ordering            = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.get_governorate_display()} — {self.street}"

    def save(self, *args, **kwargs):
        # لو العنوان ده افتراضي، شيل الافتراضي من باقي عناوينه
        if self.is_default:
            self.customer.addresses.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
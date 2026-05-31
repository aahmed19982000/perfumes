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
        extra.setdefault("role", "admin")
        return self.create_user(email, password, **extra)


class Customer(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'مدير النظام'),
        ('manager', 'المدير'),
        ('supervisor', 'المشرف'),
        ('employee', 'الموظف'),
        ('accountant', 'المحاسب'),
        ('customer', 'عميل'),
    ]

    email      = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    first_name = models.CharField(max_length=50, verbose_name="الاسم الأول")
    last_name  = models.CharField(max_length=50, verbose_name="الاسم الأخير")
    phone         = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    has_whatsapp  = models.BooleanField(default=False, verbose_name="رقم الهاتف به واتساب؟")
    avatar        = models.ImageField(upload_to="customer/avatars/", blank=True, null=True, verbose_name="الصورة الشخصية")
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer', verbose_name="الصلاحية")
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
        return f"{self.first_name} {self.last_name} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_supervisor(self):
        return self.role == 'supervisor'

    @property
    def is_employee(self):
        return self.role == 'employee'

    @property
    def is_accountant(self):
        return self.role == 'accountant'

    @property
    def can_manage_staff(self):
        return self.role == 'admin'

    @property
    def can_delete_data(self):
        return self.role in ['admin', 'manager']

    @property
    def can_manage_products(self):
        return self.role in ['admin', 'manager', 'supervisor']

    @property
    def can_add_products(self):
        return self.role in ['admin', 'manager', 'supervisor', 'employee']

    @property
    def can_view_products(self):
        return self.role in ['admin', 'manager', 'supervisor', 'employee']

    @property
    def can_manage_orders(self):
        return self.role in ['admin', 'manager', 'supervisor', 'accountant']

    @property
    def can_manage_customers(self):
        return self.role in ['admin', 'manager']

    @property
    def can_manage_coupons(self):
        return self.role in ['admin', 'manager', 'supervisor']

    @property
    def can_manage_offers(self):
        return self.role in ['admin', 'manager', 'supervisor']

    @property
    def can_manage_messages(self):
        return self.role in ['admin', 'manager']

    @property
    def can_manage_banners(self):
        return self.role in ['admin', 'manager']

    @property
    def can_manage_settings(self):
        return self.role in ['admin', 'manager']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_default_address(self):
        return self.addresses.filter(is_default=True).first()


class Governorate(models.Model):
    name_ar   = models.CharField(max_length=100, verbose_name="المحافظة بالعربي")
    name_en   = models.CharField(max_length=100, verbose_name="المحافظة بالإنجليزي")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    class Meta:
        verbose_name        = "محافظة"
        verbose_name_plural = "المحافظات"
        ordering            = ["name_ar"]

    def __str__(self):
        return self.name_ar


class City(models.Model):
    governorate   = models.ForeignKey(
        Governorate, on_delete=models.CASCADE,
        related_name="cities", verbose_name="المحافظة"
    )
    name_ar       = models.CharField(max_length=100, verbose_name="المدينة بالعربي")
    name_en       = models.CharField(max_length=100, verbose_name="المدينة بالإنجليزي")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="تكلفة الشحن")
    is_active     = models.BooleanField(default=True, verbose_name="نشط")

    class Meta:
        verbose_name        = "مدينة"
        verbose_name_plural = "المدن"
        ordering            = ["governorate", "name_ar"]

    def __str__(self):
        return f"{self.governorate.name_ar} — {self.name_ar}"


class Address(models.Model):
    customer     = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses", verbose_name="العميل")
    full_name    = models.CharField(max_length=100, verbose_name="الاسم الكامل")
    phone        = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    governorate  = models.ForeignKey(Governorate, on_delete=models.PROTECT, related_name="addresses", verbose_name="المحافظة")
    city         = models.ForeignKey(City, on_delete=models.PROTECT, related_name="addresses", verbose_name="المدينة")
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
        return f"{self.full_name} — {self.governorate.name_ar} — {self.street}"

    def save(self, *args, **kwargs):
        # لو العنوان ده افتراضي، شيل الافتراضي من باقي عناوينه
        if self.is_default:
            self.customer.addresses.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
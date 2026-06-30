from django import forms
from banners.models import Banner
from django.forms import inlineformset_factory
from products.models import Product, Category, Brand, SubCategory, ProductImage
from orders.models import Order, Coupon
from accounts.models import Customer, Governorate, City
from .models import HeaderSettings, FooterSettings

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'name_ar', 'name_en', 'description_ar', 'description_en',
            'category', 'sub_category', 'brand', 'price',
            'discount_price', 'stock', 'size', 'concentration', 'thumbnail', 'is_active', 'is_featured'
        ]
        widgets = {
            'description_ar': forms.Textarea(attrs={'rows': 3}),
            'description_en': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['has_whatsapp', 'first_name', 'last_name', 'phone', 'role', 'is_active']
        labels = {
            'has_whatsapp': 'رقم الهاتف به واتساب؟',
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'form-input'}),
            'has_whatsapp': forms.CheckboxInput(attrs={'style': 'width: 20px; height: 20px; margin-bottom: 15px;'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name_ar', 'name_en', 'image', 'is_active']
        widgets = {
            'name_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'name_en': forms.TextInput(attrs={'class': 'form-input'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
        }

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name_ar', 'name_en', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-input'}),
            'name_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'name_en': forms.TextInput(attrs={'class': 'form-input'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
        }

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'logo', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'logo': forms.FileInput(attrs={'class': 'form-input'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'order', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'وصف الصورة'}),
            'order': forms.NumberInput(attrs={'class': 'form-input'}),
        }

ProductImageFormSet = inlineformset_factory(
    Product, ProductImage, form=ProductImageForm,
    extra=3, can_delete=True
)

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title_ar', 'title_en', 'image', 'link', 'position', 'order', 'is_active']
        widgets = {
            'title_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'title_en': forms.TextInput(attrs={'class': 'form-input'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'position': forms.Select(attrs={'class': 'form-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-input'}),
        }

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'valid_from', 'valid_to', 'discount', 'active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'كود الخصم'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'مثال: 20'}),
        }

class GovernorateForm(forms.ModelForm):
    class Meta:
        model = Governorate
        fields = ['name_ar', 'name_en', 'is_active']
        widgets = {
            'name_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'name_en': forms.TextInput(attrs={'class': 'form-input'}),
        }

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['governorate', 'name_ar', 'name_en', 'shipping_cost', 'is_active']
        widgets = {
            'governorate': forms.Select(attrs={'class': 'form-input'}),
            'name_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'name_en': forms.TextInput(attrs={'class': 'form-input'}),
            'shipping_cost': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class HeaderSettingsForm(forms.ModelForm):
    class Meta:
        model = HeaderSettings
        exclude = ['updated_at']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'logo_text': forms.TextInput(attrs={'class': 'form-input'}),
            'logo_accent': forms.TextInput(attrs={'class': 'form-input'}),
            'search_placeholder_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'search_placeholder_en': forms.TextInput(attrs={'class': 'form-input'}),
            'mobile_search_placeholder_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'mobile_search_placeholder_en': forms.TextInput(attrs={'class': 'form-input'}),
            'home_label_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'home_label_en': forms.TextInput(attrs={'class': 'form-input'}),
            'categories_label_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'categories_label_en': forms.TextInput(attrs={'class': 'form-input'}),
            'categories_menu_title_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'categories_menu_title_en': forms.TextInput(attrs={'class': 'form-input'}),
            'offers_label_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'offers_label_en': forms.TextInput(attrs={'class': 'form-input'}),
            'brands_label_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'brands_label_en': forms.TextInput(attrs={'class': 'form-input'}),
            'track_order_label_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'track_order_label_en': forms.TextInput(attrs={'class': 'form-input'}),
            'about_label_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'about_label_en': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-input'})


class FooterSettingsForm(forms.ModelForm):
    class Meta:
        model = FooterSettings
        exclude = ['updated_at']
        widgets = {
            'logo_text': forms.TextInput(attrs={'class': 'form-input'}),
            'logo_accent': forms.TextInput(attrs={'class': 'form-input'}),
            'logo_image': forms.FileInput(attrs={'class': 'form-input'}),
            'tagline_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'tagline_en': forms.TextInput(attrs={'class': 'form-input'}),
            'about_text_ar': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'about_text_en': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'fb_link': forms.URLInput(attrs={'class': 'form-input'}),
            'insta_link': forms.URLInput(attrs={'class': 'form-input'}),
            'wa_link': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: 2010...'}),
            'messenger_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://m.me/...'}),
            'tiktok_link': forms.URLInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'working_hours_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'working_hours_en': forms.TextInput(attrs={'class': 'form-input'}),
            'address_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'address_en': forms.TextInput(attrs={'class': 'form-input'}),
            'copyright_text_ar': forms.TextInput(attrs={'class': 'form-input'}),
            'copyright_text_en': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-input'})


from orders.models import Offer

class OfferForm(forms.ModelForm):
    class Meta:
        model  = Offer
        fields = [
            'name_ar', 'name_en', 'description', 'offer_type',
            'is_active', 'valid_from', 'valid_to',
            'apply_to_all', 'eligible_products', 'eligible_categories',
            'buy_quantity', 'get_quantity', 'free_product',
            'discount_percent',
            'min_quantity', 'quantity_discount_percent',
            'min_order_amount',
        ]
        widgets = {
            'valid_from':          forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to':            forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description':         forms.Textarea(attrs={'rows': 3}),
            'eligible_products':   forms.SelectMultiple(attrs={'size': 6}),
            'eligible_categories': forms.SelectMultiple(attrs={'size': 4}),
        }

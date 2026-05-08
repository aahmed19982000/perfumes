from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Customer
        fields = ("email", "first_name", "last_name", "phone", "has_whatsapp")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("first_name", "last_name", "phone", "avatar")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }


from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ("full_name", "phone", "governorate", "city", "street", "building", "is_default")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "governorate": forms.Select(attrs={"class": "form-select"}),
            "city": forms.Select(attrs={"class": "form-select"}),
            "street": forms.TextInput(attrs={"class": "form-control"}),
            "building": forms.TextInput(attrs={"class": "form-control"}),
            "is_default": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

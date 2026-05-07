from django import forms
from .models import ContactMessage
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('الاسم الكامل')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('البريد الإلكتروني')}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('عنوان الرسالة')}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('اكتب رسالتك هنا...'), 'rows': 5}),
        }

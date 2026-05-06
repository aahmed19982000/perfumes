# apps/reviews/forms.py

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.Rating.choices,
        widget=forms.RadioSelect(attrs={"class": "star-radio"}),
        label="تقييمك",
    )

    class Meta:
        model   = Review
        fields  = ["rating", "title", "comment"]
        widgets = {
            "title":   forms.TextInput(attrs={
                "class":       "form-control",
                "placeholder": "عنوان مختصر للتقييم",
            }),
            "comment": forms.Textarea(attrs={
                "class":       "form-control",
                "rows":        4,
                "placeholder": "شاركنا تجربتك مع المنتج...",
            }),
        }
        labels = {
            "title":   "عنوان التقييم",
            "comment": "تعليقك",
        }
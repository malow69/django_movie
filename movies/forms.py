from django import forms

from .models import Review, Rating, RatingStar


class ReviewForm(forms.ModelForm):
    """Форма отзывов"""

    class Meta:
        model = Review
        fields = ("name", "email", "text")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control border"}),
            "text": forms.Textarea(attrs={"class": "form-control border"}),
            "email": forms.EmailInput(attrs={"class": "form-control border"})
        }


class RatingForm(forms.ModelForm):
    """Форма добавления рейтинга"""
    star = forms.ModelChoiceField(
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(), empty_label=None
    )

    class Meta:
        model = Rating
        fields = ("star",)
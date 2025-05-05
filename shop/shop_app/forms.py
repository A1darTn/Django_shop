from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Customer, Review, ShippingAddres


class LoginForm(AuthenticationForm):
    """Аутентификация пользователя"""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Имя пользователя"}
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Пароль"}
        )
    )


class RegistrationForm(UserCreationForm):
    """Регистрация пользователя"""

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Пароль"}
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Подтвердите пароль"}
        )
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Имя пользователя"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Почта"}
            ),
        }


class ReviewForm(forms.ModelForm):
    """Форма для отзыва"""

    class Meta:
        model = Review
        fields = ("text", "grade")
        widgets = {
            "text": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Ваш отзыв..."}
            ),
            "grade": forms.Select(
                attrs={"class": "form-control", "placeholder": "Ваша оценка..."}
            ),
        }


class CustomerForm(forms.ModelForm):
    """Контктная информация"""

    class Meta:
        model = Customer
        fields = ("first_name", "last_name", "email", "phone")
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваше имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваше фамилия"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Ваша почта"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваше номер телефона"}
            ),
        }


class ShippingForm(forms.ModelForm):
    """Адрес доставки"""

    class Meta:
        model = ShippingAddres
        fields = ("city", "state", "street")
        widgets = {
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваш город"}
            ),
            "state": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваша улица"}
            ),
            "street": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ваша улица, дом, квартира",
                }
            ),
        }

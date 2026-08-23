from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm as DjangoPasswordResetForm
from django.core.validators import RegexValidator
from .models import User


class IranianPhoneValidator(RegexValidator):
    regex = r'^09\d{9}$'
    message = 'شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد. مثال: ۰۹۱۲۳۴۵۶۷۸۹'


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="ایمیل")
    phone = forms.CharField(
        max_length=15,
        required=True,
        validators=[IranianPhoneValidator()],
        label="شماره موبایل",
        widget=forms.TextInput(attrs={'placeholder': '09123456789'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user


class PasswordResetForm(DjangoPasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'ایمیل خود را وارد کنید'}),
        label="ایمیل"
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'phone': 'شماره موبایل',
        }

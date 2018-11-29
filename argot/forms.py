from django import forms
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=10)
    password = forms.CharField(max_length=12)

    def clean_username(self):
        username = self.cleaned_data['username']
        if re.search('[0-9]', username) is not None:
            raise ValidationError('Cannot have numbers in username')
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if re.search('[0-9]', password) is not None:
            raise ValidationError('Cannot have numbers in password')
        return password


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=20)
    password1 = forms.CharField(max_length=20)
    password2 = forms.CharField(max_length=20)

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 4:
            raise ValidationError('Username cannot be fewer than 4 characters')
        if len(username) > 20:
            raise ValidationError('Username cannot be greater than 20 characters')
        if re.search('[0-9]', username) is not None:
            raise ValidationError('Cannot have numbers in username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(f'Username {username} already exists')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password1']
        if len(password1) < 4:
            raise ValidationError('Password cannot be fewer than 4 characters')
        if len(password1) > 20:
            raise ValidationError('Password cannot be greater than 20 characters')
        if re.search('[0-9]', password1) is not None:
            raise ValidationError('Cannot have numbers in password')
        if password1 != password2:
            raise ValidationError('Passwords do not match')
        return password1

from django import forms
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise ValidationError(f'A user has registered the '
                                  f'name: {username}')
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
            raise ValidationError('Username cannot be greater than 20 '
                                  'characters')
        if re.search('[0-9]', username) is not None:
            raise ValidationError('Cannot have numbers in username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(f'Username {username} already exists')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if len(password1) < 4:
            raise ValidationError('Password cannot be fewer than 4 characters')
        if len(password1) > 20:
            raise ValidationError('Password cannot be greater than 20 '
                                  'characters')
        if re.search('[0-9]', password1) is not None:
            raise ValidationError('Cannot have numbers in password')
        return password1

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')
        if pw1 != pw2:
            raise ValidationError('Passwords are not equal')
        if username == pw1:
            raise ValidationError('Your password cannot be your username!')


class WordListOwnerForm(forms.Form):
    list_name = forms.CharField(max_length=50)

    def clean_list_name(self):
        list_name = self.cleaned_data['list_name']
        if len(list_name) > 50:
            raise ValidationError('List names are limited to 50 characters')
        if list_name == '':
            raise ValidationError('Must enter a name for the word list')
        return list_name
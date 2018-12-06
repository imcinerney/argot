from django import forms
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    """Form to handle all log ins. Ensures that the username already exists in
    database and checks to see if the password meets the criteria for a pw
    """
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
    """Form to handle registration. Checks that password and username length
    is within the standard and that the password fulfills the requirements.
    """
    min_pass_length = 6
    max_pass_length = 20
    min_username_length = 4
    max_username_length = 30
    username = forms.CharField(max_length=max_username_length * 2)
    password1 = forms.CharField(max_length=max_pass_length * 2)
    password2 = forms.CharField(max_length=max_pass_length * 2)

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < self.min_username_length:
            raise ValidationError(f'Username cannot be fewer than '
                                  f'{self.min_username_length} characters')
        if len(username) > self.max_username_length:
            raise ValidationError(f'Username cannot be greater than '
                                  f'{self.max_username_length} characters')
        if re.search('[0-9]', username) is not None:
            raise ValidationError('Cannot have numbers in username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(f'Username {username} already exists')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if len(password1) < self.min_pass_length:
            raise ValidationError(f'Password cannot be fewer than '
                                  f'{self.min_pass_length} characters')
        if len(password1) > self.max_pass_length:
            raise ValidationError(f'Password cannot be greater than '
                                  f'{self.max_pass_length} characters')
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


class WordListForm(forms.Form):
    """Form to validate word list names. Checks that the word list name does not
    exceed the maximum word list name"""
    max_list_name_length = 50
    list_name = forms.CharField(max_length=max_list_name_length * 2)

    def clean_list_name(self):
        list_name = self.cleaned_data['list_name']
        if len(list_name) > self.max_list_name_length:
            raise ValidationError(f'List names are limited to '
                                  f'{self.max_list_name_length} characters')
        if list_name == '':
            raise ValidationError('Must enter a name for the word list')
        return list_name

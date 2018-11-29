from django import forms
from django.core.exceptions import ValidationError
import re


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

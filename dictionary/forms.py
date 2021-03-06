from django import forms
from django.core.exceptions import ValidationError
from dictionary import merriam_webster_scraper as mws
from .models import VariantWord, BaseWord


class SearchWordForm(forms.Form):
    """Form to search for a given word"""
    search_term = forms.CharField(max_length=50)

    def clean_search_term(self):
        search_term = self.cleaned_data['search_term']
        if len(search_term) > 50:
            raise ValidationError('List names are limited to 50 characters')
        if search_term == '':
            raise ValidationError('Must enter a name for the word list')
        return search_term

    def clean(self):
        cleaned_data = super().clean()
        search_term = cleaned_data.get('search_term')
        if search_term:
            variant_word_list = VariantWord.objects.all().values_list('name',
                                                                      flat=True)
            if search_term not in variant_word_list:
                found_word = mws.scrape_word(search_term, True)
                if not found_word:
                    raise ValidationError('Cannot find word in dictionary')
        else:
            raise ValidationError('Must enter a word')


class VocabTestAnswer(forms.Form):
    """Form to see if user was correct in identifying a synonym"""
    correct_choice = forms.CharField(max_length=50)
    choice = forms.CharField(max_length=50)
    base_word = forms.CharField(max_length=50)

    def clean(self):
        cleaned_data = super().clean()
        correct_answer = cleaned_data.get('correct_choice')
        choice = cleaned_data.get('choice')
        if choice is None:
            raise ValidationError('You must select an answer!')

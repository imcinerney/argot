from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from dictionary import models
from dictionary import merriam_webster_scraper as mws
from argot.forms import LoginForm
from django.contrib.auth.models import User


def home(request):
    """Returns homepage of argot and directs to three different sites

    1. Lookup Word
    2. Word Lists
    3. Log in
    """
    query = request.GET.get('search_string')
    if query:
        try:
            variant_word = models.VariantWord.objects.get(name=query)
            base_word = variant_word.base_word
            return render(request, 'dictionary/detail.html',
                          {'word': base_word})
        except models.VariantWord.DoesNotExist:
            if mws.scrape_word(query):
                variant_word = models.VariantWord.objects.get(name=query)
                base_word = variant_word.base_word
                return render(request, 'dictionary/detail.html',
                              {'word': base_word})
            else:
                return render(request, 'argot/no_word_found.html',
                              {'word' : query})
    return render(request, 'argot/home.html')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = User.objects.create_user(username=username, password=password)
            return HttpResponse(f'yay valid form, user is {username}, pw is: {password}')
        else:
            return HttpResponse(f'boo invalid form error: {form.errors}')
    else:
        return HttpResponse(f'You got here without posting')

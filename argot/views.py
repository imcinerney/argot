from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from dictionary import models
from dictionary import merriam_webster_scraper as mws
from argot.forms import LoginForm, RegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


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


def register(request):
    return render(request, 'argot/register.html')


def create_user(request):
    """Registers users, validates password and username requirements, and then
    logs in
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            username = form.cleaned_data['username']
            user = User.objects.create_user(username=username,
                                            password=password)
            login(request, user)
            return render(request, 'argot/successful_registration.html')
        else:
            return render(request, 'argot/registration_error.html',
                                   {'form': form})
    else:
        return HttpResponseRedirect('/')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse('Incorrect pw, please guess again')
        else:
            return HttpResponse(f'boo invalid form error: {form.errors}')
    else:
        return HttpResponseRedirect('/')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

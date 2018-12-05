from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from dictionary import models
from dictionary import merriam_webster_scraper as mws
from argot.forms import LoginForm, RegistrationForm, WordListForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from dictionary.forms import SearchWordForm


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


def word_lists(request):
    if request.user.is_authenticated:
        user = request.user
        word_lists = user.wordlist_set.all()
        return render(request, 'argot/word_lists.html',
                      {'word_lists': word_lists})
    else:
        return HttpResponseRedirect('/')


def create_word_list(request):
    return render(request, 'argot/create_word_list.html')


def gen_word_list(request):
    if request.method == 'POST' and request.user.is_authenticated:
        form = WordListForm(request.POST)
        if form.is_valid():
            list_name = form.cleaned_data['list_name']
            word_owner = models.WordList(list_name=list_name, user=request.user)
            word_owner.save()
            word_owner_id = word_owner.id
            return HttpResponseRedirect(f'dictionary/word_list/{word_owner_id}')
        else:
            return HttpResponse(f'Issues with list_name:{form.errors}')
    else:
        return HttpResponseRedirect

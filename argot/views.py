from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from dictionary import models
from argot.forms import LoginForm, RegistrationForm, WordListForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from dictionary.forms import SearchWordForm
from dictionary import merriam_webster_scraper as mws


def home(request):
    """Returns homepage of argot.

    Greets user and gives an explanation of what argot is. Allows user to
    look up words. Eventually will offer a number of practice word lists to play
    with. Allows user to login or to register.
    """
    query = request.GET.get('search_term')
    word_list = None
    if request.user.is_authenticated:
        word_list = request.user.profile.active_word_list
    if query:
        form = SearchWordForm(request.GET)
        if form.is_valid():

            search_term = form.cleaned_data['search_term']
            base_word = models.VariantWord.objects.get(name=search_term) \
                              .base_word
            if base_word.searched_synonym == False:
                mws.scrape_word(base_word.name, True)
            if word_list is not None:
                word_list.add_word(base_word)
            return render(request, 'dictionary/detail.html',
                          {'word': base_word})
        else:
            return render(request, 'argot/no_word_found.html',
                          {'word' : query})
    return render(request, 'argot/home.html')


def register(request):
    """Registration page, makes user input username and password"""
    if request.user.is_authenticated == False:
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                username = form.cleaned_data['username']
                user = User.objects.create_user(username=username,
                                                password=password)
                login(request, user)
                return render(request, 'argot/successful_registration.html')
            else:
                errors = form.errors
                return render(request, 'argot/registration_error.html',
                                       {'errors': errors})
        else:
            return render(request, 'argot/register.html')
    else:
        return HttpResponseRedirect('/')


def user_login(request):
    """Handles log in. Makes sure that the username is in the database and then
    authenticates log in"""
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
                return HttpResponse('Incorrect pw, please try again')
        else:
            return HttpResponse(f'boo invalid form error: {form.errors}')
    else:
        return HttpResponseRedirect('/')


def user_logout(request):
    """Logs out user and returns home"""
    logout(request)
    return HttpResponseRedirect('/')


def top_word_lists(request):
    """Displays the top 5 most viewed word lists"""
    top_word_lists = models.WordList.objects.filter(is_public=True) \
                           .order_by('-view_count')[:5]
    return render(request, 'argot/top_word_lists.html',
                  {'top_word_lists' : top_word_lists})

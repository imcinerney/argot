from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from dictionary import models
from dictionary import merriam_webster_scraper as mws
from argot.forms import LoginForm, RegistrationForm, WordListForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from dictionary.forms import SearchWordForm


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
                return render(request, 'argot/registration_error.html',
                                       {'form': form})
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


def word_lists(request):
    """Display the name of all word lists and the number of words in them"""
    if request.user.is_authenticated:
        user = request.user
        word_lists = user.wordlist_set.all()
        return render(request, 'argot/word_lists.html',
                      {'word_lists': word_lists})
    else:
        return HttpResponseRedirect('/')


def create_word_list(request):
    """User can input name of word list to create new word list"""
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = WordListForm(request.POST)
            if form.is_valid():
                list_name = form.cleaned_data['list_name']
                word_list = models.WordList(list_name=list_name,
                                            user=request.user)
                word_list.save()
                word_list_id = word_list.id
                return HttpResponseRedirect(f'dictionary/word_list/'
                                            f'{word_list_id}')
            else:
                return HttpResponse(f'Issues with list_name:{form.errors}')
        else:
            return render(request, 'argot/create_word_list.html')
    return HttpResponseRedirect('/')

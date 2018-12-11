from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from . import models
from dictionary.forms import SearchWordForm
from argot.forms import WordListForm
import random
from dictionary import merriam_webster_scraper as mws
import threading


def detail(request, base_word_id):
    """Displays the definition page for a baseword"""
    word = get_object_or_404(models.BaseWord, pk=base_word_id)
    return render(request, 'dictionary/detail.html', {'word': word})


def view_word_list(request, word_list_id):
    """Displays list of all words and lets user add new words.

    Currently if a user is not logged in and the word list isn't hers, she will
    not be able to see the list. Will eventually change to have the option to
    hide / show word lists to non-owners. Maybe also have the option to allow
    other users to add as well?
    """
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    if request.user.is_authenticated:
        list_owner = word_list.user
        if list_owner != request.user:
            return HttpResponseRedirect('/')
        else:
            profile = request.user.profile
            profile.active_word_list = word_list
            profile.save()
            return render(request, 'dictionary/view_word_list.html',
                          {'word_list' : word_list})
    else:
        return HttpResponseRedirect('/')


def add_words_to_word_list(request, word_list_id):
    """Handles adding words to the word list"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    if request.method == 'POST' and request.user.is_authenticated:
        form = SearchWordForm(request.POST)
        if form.is_valid():
            word = form.cleaned_data['search_term']
            base_word = models.VariantWord.objects.get(name=word).base_word
            wl_entry, _ = models.WordListEntry.objects \
                                .get_or_create(word_list=word_list,
                                               word=base_word)
            return HttpResponseRedirect(reverse('dictionary:view_word_list',
                                                args=(word_list_id,)))
        else:
            return HttpResponse('No matching word')
    else:
        return HttpResponseRedirect('/')


def delete_word_list(request, word_list_id):
    """Handles deleting a word list. Must be the owner in order to delete"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    if request.user.is_authenticated:
        list_owner = word_list.user
        if list_owner != request.user:
            return HttpResponseRedirect('/')
        else:
            word_list.delete()
            return HttpResponseRedirect(reverse('word_lists'))
    else:
        return HttpResponseRedirect('/')


def change_word_list_name(request, word_list_id):
    """Handles changing the name of the word list. Only owner can change name"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    if request.user.is_authenticated:
        if request.method == 'POST':
            list_owner = word_list.user
            form = WordListForm(request.POST)
            if list_owner == request.user and form.is_valid():
                word_list.list_name = form.cleaned_data['list_name']
                word_list.save()
                return HttpResponseRedirect(reverse('dictionary:view_word_list',
                                                    args=(word_list_id,)))
            else:
                return HttpResponseRedirect('/')
        else:
            return render(request, 'dictionary/change_word_list_name.html',
                          {'word_list': word_list})
    return render(request, 'dictionary/change_word_list_name.html')


def play_game(request, word_list_id):
    """Handles playing a game for a word list"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    entry_list = word_list.entries_list()
    synonym_dict = {}
    for entry in entry_list:
        if entry.searched_synonym == False:
            mws.scrape_word(entry.name, True)
        synonym_list = entry.synonym_set.all()
        synonyms = [synonym.synonym.name for synonym in synonym_list]
        synonym_dict[entry] = synonyms
    choice = random.choice(entry_list)
    synonyms = synonym_dict[choice]
    return render(request, 'dictionary/play_game.html',
                  {'word_list': word_list, 'choice': choice,
                   'synonyms' : synonyms})

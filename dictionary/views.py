from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from . import models
from dictionary.forms import SearchWordForm, VocabTestAnswer
from argot.forms import WordListForm
import random
from dictionary import merriam_webster_scraper as mws
from django.db.models import F


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
            word_list.view_count += 1
            profile = request.user.profile
            profile.active_word_list = word_list
            profile.save()
            word_list.save()
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


def _return_synonym_dict(entry_list):
    """Handles generating the synonym_dict for the game"""
    synonym_dict = {}
    for entry in entry_list:
        if entry.searched_synonym == False:
            mws.scrape_word(entry.name, True)
        synonym_list = entry.synonym_set.all() \
                            .annotate(s_base_word_id=F('synonym__base_word'))
        synonym_dict[entry] = synonym_list
    return synonym_dict


def _return_all_synonyms():
    """Queries for all the list of synonyms with the baseword ids as well"""
    all_synonyms = models.Synonym.objects.all() \
                         .annotate(s_base_word_id=F('synonym__base_word')) \
                         .annotate(synonym_name=F('synonym__name')) \
                         .values_list('synonym_name', flat=True)
    return all_synonyms


def play_game(request, word_list_id):
    """User will be asked to select the correct synonym out of 4 possible words

    Takes all synonyms of a random word and choses one of the synonym as the
    correct synonym. Three incorrect synonyms are selected by excluding all
    synonyms for the selected word and then picking three synonyms from the db
    as the invalid answers.
    """
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    if request.method == 'POST':
        form = VocabTestAnswer(request.POST)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            correct_choice = form.cleaned_data['correct_choice']
            if choice == correct_choice:
                msg = 'Nice! Correct synonym'
            else:
                msg = f'Wrong answer. The correct synonym is: {correct_choice}'
        else:
            msg = 'You have to select an answer!'
    else:
        msg = ''
    entry_list = word_list.entries_list()
    synonym_dict = _return_synonym_dict(entry_list)
    all_synonyms = _return_all_synonyms()
    test_word = random.choice(entry_list)
    choice_synonyms = synonym_dict[test_word]
    subq1 = (choice_synonyms.values('s_base_word_id'))
    non_choice_synonyms = list(all_synonyms
                                   .exclude(s_base_word_id__in=subq1)
                                   .values_list('synonym_name', flat=True)
                              )
    choice_synonym = random.choice(choice_synonyms).synonym.name
    non_choice_answers = random.sample(non_choice_synonyms, k=3)
    choices = [choice_synonym] + non_choice_answers
    random.shuffle(choices)
    return render(request, 'dictionary/play_game.html',
                  {'word_list': word_list, 'test_word': test_word,
                   'choices': choices,
                   'choice_synonym' : choice_synonym,
                   'non_choice_synonyms': non_choice_synonyms,
                   'msg' : msg,
                   })

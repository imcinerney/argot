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
    if not word.searched_synonym:
        mws.scrape_word(word.name, True)
    return render(request, 'dictionary/detail.html', {'word': word})


def view_word_list(request, word_list_id):
    """Displays list of all words and lets user add new words."""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    is_public = word_list.is_public
    if is_public or (word_list.user == request.user):
        return _display_word_list(request, word_list_id)
    else:
        return HttpResponseRedirect('/')


def _display_word_list(request, word_list_id):
    """Displays word_list, increased view count, and turns to active if owner"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    word_list.view_count += 1
    word_list.save()
    if word_list.user == request.user:
        profile = request.user.profile
        profile.active_word_list = word_list
        profile.save()
    return render(request, 'dictionary/view_word_list.html',
                  {'word_list' : word_list})


def create_word_list(request):
    """User can input name of word list to create new word list"""
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = WordListForm(request.POST)
            if form.is_valid():
                list_name = form.cleaned_data['list_name']
                is_public = form.cleaned_data['is_public']
                word_list = models.WordList(list_name=list_name,
                                            user=request.user,
                                            is_public=is_public)
                word_list.save()
                word_list_id = word_list.id
                return HttpResponseRedirect(f'/dictionary/word_list/'
                                            f'{word_list_id}')
            else:
                return HttpResponse(f'Issues with list_name:{form.errors}')
        else:
            return render(request, 'dictionary/create_word_list.html')
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


def view_user_word_lists(request):
    """Display the name of all word lists and the number of words in them"""
    if request.user.is_authenticated:
        user = request.user
        word_lists = user.wordlist_set.all()
        return render(request, 'dictionary/view_user_word_lists.html',
                      {'word_lists': word_lists})
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
            return HttpResponseRedirect(
                reverse('dictionary:view_user_word_lists'))
    else:
        return HttpResponseRedirect('/')


def change_word_list_name(request, word_list_id):
    """Handles changing the name of the word list. Only owner can change name"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    if request.user.is_authenticated:
        list_owner = word_list.user
        if list_owner == request.user and request.method == 'POST':
            form = WordListForm(request.POST)
            if form.is_valid():
                word_list.list_name = form.cleaned_data['list_name']
                word_list.save()
            return HttpResponseRedirect(reverse('dictionary:edit_list',
                                                args=(word_list_id,)))
        else:
            return HttpResponseRedirect(reverse('dictionary:edit_list',
                                                    args=(word_list_id,)))
    return HttpResponseRedirect('/')


def change_privacy(request, word_list_id):
    """Changes the privacy of the word list"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    list_owner = word_list.user
    if request.user == list_owner:
        privacy = word_list.is_public
        word_list.is_public = not privacy
        word_list.save()
        return HttpResponseRedirect(reverse('dictionary:edit_list',
                                            args=(word_list_id,)))
    else:
        return HttpResponseRedirect(reverse('dictionary:view_user_word_lists'))


def edit_list(request, word_list_id):
    """Page to allow user to change word list name, privacy, or delete words"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    list_owner = word_list.user
    if request.user == list_owner:
        return render(request, 'dictionary/edit_word_list.html',
                      {'word_list': word_list})
    else:
        return HttpResponseRedirect(reverse('dictionary:view_word_list',
                                            args=(word_list_id,)))


def remove_words(request, word_list_id):
    """Handles removing words from word list"""
    word_list = get_object_or_404(models.WordList, pk=word_list_id)
    list_owner = word_list.user
    if request.user == list_owner and request.method == 'POST':
        for word_entry in word_list.wordlistentry_set.all():
            lookup_string = 'words_to_delete' + str(word_entry.id)
            try:
                delete = request.POST[lookup_string]
                word_entry.delete()
            except KeyError:
                pass
        return HttpResponseRedirect(reverse('dictionary:edit_list',
                                            args=(word_list_id,)))
    else:
        return HttpResponseRedirect(reverse('dictionary:view_word_list',
                                            args=(word_list_id,)))


def _return_synonym_dict(entry_list):
    """Handles generating the synonym_dict for the game"""
    synonym_dict = {}
    for entry in entry_list:
        if entry.searched_synonym == False:
            mws.scrape_word(entry.name, True)
        synonym_list = entry.synonym_set.all() \
                            .annotate(s_base_word_id=F('synonym__base_word'))
        if len(synonym_list) != 0:
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
            test_word = form.cleaned_data['base_word']
            base_word = models.BaseWord.objects.get(name=test_word)
            accuracy, _  = models.UserAccuracy.objects \
                                 .get_or_create(base_word=base_word,
                                                user=request.user)
            base_word.total_guesses += 1
            accuracy.total_guesses += 1
            if choice == correct_choice:
                msg = 'Nice! Correct synonym'
                base_word.correct_guesses += 1
                accuracy.correct_guesses += 1
            else:
                msg = f'Wrong answer. The correct synonym is: {correct_choice}'
            base_word.save()
            accuracy.save()
        else:
            msg = 'You have to select an answer!'
    else:
        msg = ''
    entry_list = word_list.entries_list()
    if len(entry_list) < 5:
        return HttpResponse('You must have at least five entries to practice')
    synonym_dict = _return_synonym_dict(entry_list)
    if len(synonym_dict) == 0:
        return HttpResponse('None of your words have synonyms to test')
    #some entries don't have synonyms
    entry_list = list(synonym_dict.keys())
    all_synonyms = _return_all_synonyms()
    test_word = random.choice(entry_list)
    choice_synonyms = synonym_dict[test_word]
    subq1 = (choice_synonyms.values('s_base_word_id'))
    non_choice_synonyms = list(all_synonyms
                                   .exclude(s_base_word_id__in=subq1)
                                   .values_list('synonym_name', flat=True)
                              )
    choice_synonym = random.choice(choice_synonyms).synonym.name
    try:
        non_choice_answers = random.sample(non_choice_synonyms, k=3)
    except ValueError:
        raise ValueError('You must add more entries to the database before'
                         ' starting a game')
    choices = [choice_synonym] + non_choice_answers
    random.shuffle(choices)
    return render(request, 'dictionary/play_game.html',
                  {'word_list': word_list, 'test_word': test_word,
                   'choices': choices,
                   'choice_synonym' : choice_synonym,
                   'non_choice_synonyms': non_choice_synonyms,
                   'msg' : msg,
                   })

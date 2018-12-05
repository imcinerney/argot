from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from . import models
from dictionary.forms import SearchWordForm
from argot.forms import WordListForm


class IndexView(generic.ListView):
    template_name = 'dictionary/index.html'
    context_object_name = 'latest_words_added'

    def get_queryset(self):
        """Return last five added dictionary words"""
        return models.BaseWord.objects.order_by('-pk')[:5]


class ResultsView(generic.DetailView):
    model = models.BaseWord
    template_name = 'dictionary/results.html'


def detail(request, base_word_id):
    word = get_object_or_404(models.BaseWord, pk=base_word_id)
    return render(request, 'dictionary/detail.html', {'word': word})


def view_word_list(request, word_list_id):
    """Displays list of all words and lets user add new words"""
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
    """Handles changing the name of the word list"""
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

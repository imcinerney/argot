from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from . import models
from dictionary.forms import SearchWordForm


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


def view_word_list(request, word_owner_id):
    """Displays list of all words and lets user add new words"""
    word_list_owner = get_object_or_404(models.WordListOwner, pk=word_owner_id)
    return render(request, 'dictionary/view_word_list.html',
                  {'word_list_owner' : word_list_owner})


def add_words_to_word_list(request, word_owner_id):
    word_list_owner = get_object_or_404(models.WordListOwner, pk=word_owner_id)
    if request.method == 'POST' and request.user.is_authenticated:
        form = SearchWordForm(request.POST)
        if form.is_valid():
            word = form.cleaned_data['search_term']
            base_word = models.VariantWord.objects.get(name=word).base_word
            wl_entry, _ = models.WordList.objects \
                                .get_or_create(word_list=word_list_owner,
                                               word=base_word)
            return HttpResponseRedirect(reverse('dictionary:view_word_list',
                                                args=(word_owner_id,)))
        else:
            return HttpResponse('No matching word')
    else:
        return HttpResponseRedirect('/')


def delete_word_list(request, word_owner_id):
    word_list_owner = get_object_or_404(models.WordListOwner, pk=word_owner_id)
    if request.user.is_authenticated:
        list_owner = word_list_owner.user
        if list_owner != request.user:
            raise HttpResponse('/')
        else:
            word_list_owner.delete()
            return HttpResponseRedirect(reverse('word_lists'))
    else:
        return HttpResponseRedirect('/')

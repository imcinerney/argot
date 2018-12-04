from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from . import models


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


def add_words_to_word_list(request):
    if request.method == 'POST' and request.user.is_authenticated:
        form = WordListOwnerForm(request.POST)
        if form.is_valid():
            return HttpResponse('Word matches')
        else:
            return HttpResponse('No matching word')
    else:
        return HttpResponseRedirect('/')

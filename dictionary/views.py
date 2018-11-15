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

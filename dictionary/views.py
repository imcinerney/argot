from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from . import models


def index(request):
    latest_words_added = models.BaseWord.objects.order_by('-id')[:5]
    context = {
        'latest_words_added': latest_words_added,
    }
    return render(request, 'dictionary/index.html', context)


def detail(request, base_word_id):
    word = get_object_or_404(models.BaseWord, pk=base_word_id)
    return render(request, 'dictionary/detail.html', {'word': word})


def results(request, base_word_id):
    response = 'You are looking at the name of base_word %s'
    return HttpResponse(response % base_word_id)


def vote(request, base_word_id):
    return HttpResponse(f'You are voting on: {base_word_id}')

from django.urls import path
from . import views

app_name = 'dictionary'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:base_word_id>/', views.detail, name='detail'),
    path('<int:base_word_id>/results/', views.results, name='results'),
    path('<int:base_word_id>/vote/', views.vote, name='vote'),
]

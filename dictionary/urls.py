from django.urls import path
from . import views

app_name = 'dictionary'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:base_word_id>/', views.detail, name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('word_list/<int:word_owner_id>/', views.view_word_list,
         name='view_word_list'),
    path('word_list<int:word_owner_id>/add_words_to_word_list',
          views.add_words_to_word_list, name='add_words_to_word_list'),
]

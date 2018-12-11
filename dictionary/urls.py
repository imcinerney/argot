from django.urls import path
from . import views

app_name = 'dictionary'
urlpatterns = [
    path('<int:base_word_id>/', views.detail, name='detail'),
    path('word_list/<int:word_list_id>/', views.view_word_list,
         name='view_word_list'),
    path('word_list<int:word_list_id>/add_words_to_word_list',
          views.add_words_to_word_list, name='add_words_to_word_list'),
    path('word_list/delete/<int:word_list_id>', views.delete_word_list,
         name='delete_word_list'),
    path('word_list/<int:word_list_id>/change_name',
        views.change_word_list_name, name='change_word_list_name'),
    path('word_list/<int:word_list_id>/load_game', views.load_game,
         name='load_game'),
]

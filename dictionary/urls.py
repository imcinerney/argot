from django.urls import path
from . import views

app_name = 'dictionary'
urlpatterns = [
    path('<int:base_word_id>/', views.detail, name='detail'),
    path('word_list/<int:word_list_id>/', views.view_word_list,
         name='view_word_list'),
    path('word_list/<int:word_list_id>/add_words_to_word_list',
          views.add_words_to_word_list, name='add_words_to_word_list'),
    path('word_list/delete/<int:word_list_id>', views.delete_word_list,
         name='delete_word_list'),
    path('word_list/<int:word_list_id>/change_name',
        views.change_word_list_name, name='change_word_list_name'),
    path('word_list/<int:word_list_id>/play_game', views.play_game,
         name='play_game'),
    path('word_list/<int:word_list_id>/change_privacy', views.change_privacy,
         name='change_privacy'),
    path('word_list/view_user_word_lists', views.view_user_word_lists,
         name='view_user_word_lists'),
    path('word_list/create_word_list', views.create_word_list,
         name='create_word_list'),
    path('word_list/<int:word_list_id>/edit_list', views.edit_list,
         name='edit_list'),
]

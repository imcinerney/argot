from django.urls import path
from . import views

app_name = 'dictionary'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:base_word_id>/', views.detail, name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
]

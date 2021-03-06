"""argot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views as home_views


urlpatterns = [
    path('', home_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('dictionary/', include('dictionary.urls')),
    path('register/', home_views.register, name='register'),
    path('user_login', home_views.user_login, name='user_login'),
    path('user_logout', home_views.user_logout, name='user_logout'),
    path('top_word_lists', home_views.top_word_lists, name='top_word_lists'),
]

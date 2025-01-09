#File: community/urls.py

from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('naver-book-json/', views.naver_book_json, name='naver-book-json'),
    path('naver-book-template/', views.naver_book_template, name='naver-book-template'),
]

#File: community/urls.py

from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('naver-book-json/', views.naver_book_json, name='naver-book-json'),
    path('naver-book-template/', views.naver_book_template, name='naver-book-template'),
    path('naver-books/', views.naver_books, name='naver_books'),
    path('post/', views.post, name='post'),
    path('login/', views.login, name='login'),
    path('', views.home, name='home'),
]

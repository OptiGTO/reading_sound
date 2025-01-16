#File: community/urls.py

from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('naver-book-json/', views.naver_book_json, name='naver-book-json'),
    path('naver-book-template/', views.naver_book_template, name='naver-book-template'),
    path('naver-books/', views.naver_books, name='naver_books'),
    path('post/', views.post_view, name='post'),
    path('login/', views.login_view, name='login'),
    path('reading_meeting/', views.reading_meeting, name='reading_meeting'),
    path('review_event/', views.review_event, name='review_event'),
    path('booktalk/', views.booktalk, name='booktalk'),
    path('your_content/', views.your_content, name='your_content'),
    path('parrhesia/', views.parrhesia, name='parrhesia'),
   path('', views.home_view, name='home'),
]

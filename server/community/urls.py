#File: community/urls.py

from django.urls import path
from . import views
from community.admin_views import book_search_view, book_add_view

app_name = 'community'

urlpatterns = [
    path('naver-book-json/', views.naver_book_json, name='naver-book-json'),
    path('naver-book-template/', views.naver_book_template, name='naver-book-template'),
    path('naver-books/', views.naver_books, name='naver_books'),
    path('post/', views.post_view, name='post'),
    path('login/', views.login_view, name='login'),
    path('admin/books/search/', book_search_view, name='admin_books_search'),
    path('admin/books/add/', book_add_view, name='admin_books_add'),
    path('', views.home_view, name='home'),
]

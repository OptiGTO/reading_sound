from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('naver-book-search/', views.naver_book_search, name='naver-book-search'),
]

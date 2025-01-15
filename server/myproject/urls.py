
#File: myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from community.admin_views import book_search_view, book_add_view

urlpatterns = [
    path('admin/books/search/', book_search_view, name='admin_books_search'),
    path('admin/books/add/', book_add_view, name='admin_books_add'),
    path('admin/', admin.site.urls),
    path('', include('community.urls')),  # route to the community app
]

from django.shortcuts import render
from .models import Book

def home_view(request):
    # Simple example: fetch all books from DB
    books = Book.objects.all()
    return render(request, 'community/index.html', {'books': books})

from django.contrib import admin
from .models import Post, Book
# Register your models here.

admin.site.register(Book)
admin.site.register(Post)
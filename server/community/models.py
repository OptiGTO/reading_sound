from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    # For storing Google Books thumbnail URL, etc.
    thumbnail_url = models.URLField(blank=True, null=True)
    # date_added or other fields...

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # etc.

    def __str__(self):
        return self.title

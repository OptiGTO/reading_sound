from django.contrib import admin
from .models import Post, Book
# Register your models here.

admin.site.register(Post)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "pubdate")

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context["admin_books_search_url"] = "/admin/books/search/"
        return super().changelist_view(request, extra_context=extra_context)

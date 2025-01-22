from django.contrib import admin
from .models import Post, Book, EventPost, ReadingGroupPost, ReadingTipPost
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "writer", "category", "created_at",)

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context["admin_books_search_url"] = "/admin/books/search/"
        return super().changelist_view(request, extra_context=extra_context)
    


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "pubdate",)

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context["admin_books_search_url"] = "/admin/books/search/"
        return super().changelist_view(request, extra_context=extra_context)



@admin.register(EventPost)
class EventPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'event_date', 'is_active')
    list_filter = ('is_active', 'event_date')
    search_fields = ('title', 'content')

@admin.register(ReadingGroupPost)
class ReadingGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'meeting_time', 'is_active')
    list_filter = ('is_active', 'meeting_time')
    search_fields = ('title', 'content')

@admin.register(ReadingTipPost)
class ReadingTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('title', 'content')
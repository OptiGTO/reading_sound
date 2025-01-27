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
    list_display = ('title', 'author', 'event_date', 'is_active', 'is_pinned', 'is_deleted')
    list_filter = ('is_active', 'event_date', 'is_pinned', 'is_deleted')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'is_pinned')

@admin.register(ReadingGroupPost)
class ReadingGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'meeting_time', 'is_active', 'is_pinned', 'is_deleted')
    list_filter = ('is_active', 'meeting_time', 'is_pinned', 'is_deleted')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'is_pinned')

@admin.register(ReadingTipPost)
class ReadingTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_active', 'is_pinned', 'is_deleted')
    list_filter = ('is_active', 'category', 'is_pinned', 'is_deleted')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'is_pinned')
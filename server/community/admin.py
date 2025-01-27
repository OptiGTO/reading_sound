from django.contrib import admin
from django.db import models
from .models import Post, Book, EventPost, ReadingGroupPost, ReadingTipPost, PostImage
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "writer", "category", "created_at", "book")
    list_display_links = ("title", "writer", "category", "created_at", "book")
    ordering = ("-created_at",)


    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context["admin_books_search_url"] = "/admin/books/search/"
        return super().changelist_view(request, extra_context=extra_context)
    

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image', 'created_at')
    list_filter = ('post', 'created_at')
    search_fields = ('post__title',)
    ordering = ('post', 'created_at')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("priority", "title", "author", "publisher", "pubdate", "isbn")
    list_display_links = ("title",)
    list_editable = ("priority",)
    ordering = ("priority", "-pubdate")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by(
            models.F('priority').asc(nulls_last=True),
            '-pubdate'
        )

    # 검색 기능 추가
    def changelist_view(self, request, extra_context=None): #
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


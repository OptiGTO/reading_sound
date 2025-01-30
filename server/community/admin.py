from django.contrib import admin
from django.db import models
from .models import (
    GeneralPost, Book, BookEventPost, BookReviewEventPost, 
    ReadingGroupPost, ReadingTipPost, PostImage, PostTag
)
# Register your models here.

@admin.register(GeneralPost)
class GeneralPostAdmin(admin.ModelAdmin):
    list_display = ("title", "writer", "category", "created_at", "book")
    list_display_links = ("title", "writer", "category", "created_at", "book")
    ordering = ("-created_at", "is_pinned")

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context["admin_books_search_url"] = "/admin/books/search/"
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(BookReviewEventPost)
class BookReviewEventPostAdmin(admin.ModelAdmin):
    list_display = ("title", "writer", "category", "created_at", "book")
    list_display_links = ("title", "writer", "category", "created_at", "book")
    ordering = ("-created_at","is_pinned")

#----------------------------------이미지 관련----------------------------------
@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image', 'created_at')
    list_filter = ('post', 'created_at',)
    search_fields = ('post__title',)
    ordering = ('post', 'created_at')

#----------------------------------책 관리자 권한 관련----------------------------------
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

#----------------------------------사이드바 관련----------------------------------
@admin.register(BookEventPost)
class BookEventPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'event_start_date', 'is_active', 'is_pinned')
    list_filter = ('is_active', 'event_start_date', 'is_pinned', 'is_deleted')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'is_pinned')

@admin.register(ReadingGroupPost)
class ReadingGroupPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'event_date', 'is_active', 'is_pinned')
    list_filter = ('is_active', 'event_date', 'is_pinned', 'is_deleted')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'is_pinned')

@admin.register(ReadingTipPost)
class ReadingTipPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'tip_category', 'is_active', 'is_pinned')
    list_filter = ('is_active', 'tip_category', 'is_pinned', 'is_deleted')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'is_pinned')


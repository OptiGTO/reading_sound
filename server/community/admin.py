from django.contrib import admin
from django.db import models
from .models import (
    GeneralPost, Book, BookReviewEventPost, PersonalBookEventPost,
    BookTalkEventPost, ReadingGroupPost, ReadingTipPost, PostImage, PostTag, Comment
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

@admin.register(PersonalBookEventPost)
class PersonalBookEventPostAdmin(admin.ModelAdmin):
    list_display = ("title", "writer", "category", "created_at", "book")
    list_display_links = ("title", "writer", "category", "created_at", "book")
    ordering = ("-created_at", "is_pinned")

@admin.register(BookTalkEventPost)
class BookTalkEventPostAdmin(admin.ModelAdmin):
    list_display = ("title", "writer", "category", "created_at", "book")
    list_display_links = ("title", "writer", "category", "created_at", "book")
    ordering = ("-created_at", "is_pinned")

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

#----------------------------------댓글 관리자 권한 관련----------------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_post', 'get_writer', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)
    ordering = ('-created_at',)

    def get_post(self, obj):
        content_object = obj.content_object
        return getattr(content_object, 'title', 'N/A')
    get_post.short_description = '게시글'

    def get_writer(self, obj):
        content_object = obj.content_object
        writer = getattr(content_object, 'writer', None)
        return str(writer) if writer else 'N/A'
    get_writer.short_description = '작성자'

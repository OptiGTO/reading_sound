from django.contrib import admin
from django.db import models
from .models import (
    GeneralPost, Book, BookReviewEventPost, PersonalBookEventPost,
    BookTalkEventPost, ReadingGroupPost, ReadingTipPost, PostImage, PostTag, Comment, BookGenre, Like
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
    list_display = ('get_post', 'image', 'created_at')
    list_filter = ('created_at',)  # 'post'는 GenericForeignKey이므로 제외
    # search_fields는 기본적으로 메서드를 직접 검색 대상으로 사용할 수 없으므로, 
    # 필요하다면 다른 방법(예: 대상 모델의 필드를 통해 검색)을 고려해야 합니다.
    ordering = ('created_at',)

    def get_post(self, obj):
        # obj.post는 GenericForeignKey로 연결된 객체
        # 예를 들어, 게시글 객체의 title을 반환하도록 할 수 있습니다.
        return getattr(obj.post, 'title', 'N/A') if obj.post else "N/A"
    get_post.short_description = "게시글"
#----------------------------------책 관리자 권한 관련----------------------------------


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("priority", "title", "author", "publisher", "pubdate", "isbn", 'genre')
    list_display_links = ("title",)
    list_editable = ("priority",)
    ordering = ("priority", "-pubdate")



    list_filter = ("is_recommended", "is_active", "genre")


    # 우선순위 높은(숫자 낮은) 책부터 정렬
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

#----------------------------------좋아요 관리자 권한 관련----------------------------------
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('get_content_object', 'get_user_name', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'content_type__model')
    ordering = ('-created_at',)

    def get_content_object(self, obj):
        """좋아요가 달린 객체(게시글/책)의 제목을 반환"""
        content_object = obj.content_object
        return getattr(content_object, 'title', 'N/A')
    get_content_object.short_description = '대상'

    def get_user_name(self, obj):
        """좋아요를 누른 사용자의 이름을 반환"""
        return obj.user.username if obj.user else 'N/A'
    get_user_name.short_description = '사용자'





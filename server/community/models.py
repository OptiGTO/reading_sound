# File: community/models.py

from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField  # 파일 업로드 지원
from django.contrib.auth import get_user_model             # User 모델을 가져오는 방식 수정

User = get_user_model()                                   # 파일 상단에서 한 번만 정의

# 책 모델
class Book(models.Model):
    # NAVER Book API에서 받아올 수 있는 주요 필드 예시
    isbn         = models.CharField(max_length=13, unique=True, null=True)
    title        = models.CharField(max_length=200)
    author       = models.CharField(max_length=100, blank=True, null=True)
    publisher    = models.CharField(max_length=100, blank=True, null=True)
    pubdate      = models.CharField(max_length=20, blank=True, null=True)  # YYYYMMDD 형태가 올 수 있음
    thumbnail_url= models.URLField(blank=True, null=True)
    link         = models.URLField(blank=True, null=True)  # NAVER 도서 링크

    priority = models.PositiveIntegerField(
        default=0, 
        null=True, 
        blank=True,
        verbose_name='우선순위', 
        help_text='낮은 숫자가 더 높은 우선순위(1 > 2), 미설정시 자동 정렬'
    )  # 우선순위 필드 추가

    
    def __str__(self):
        return self.title

class PostCategory(models.TextChoices):
    ESSAY   = 'essay',   '에세이'
    POETRY  = 'poetry',  '시'
    NOVEL   = 'novel',   '소설'
    NONLIT  = 'nonlit',  '비문학'


class Post(models.Model):
    title       = models.CharField(max_length=200) 
    content     = RichTextUploadingField()  
    writer      = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 글 태그(분류)
    category    = models.CharField(
        max_length=10,
        choices=PostCategory.choices,
        default=PostCategory.ESSAY
    )
    
    # 어떤 책 관련 글인지 연결
    book        = models.ForeignKey('Book', on_delete=models.CASCADE, null=True, blank=True)
    
    # 이미지 첨부
    image       = models.ImageField(upload_to='post_images/', blank=True, null=True)

    # 작성일 (자동 기록)
    created_at  = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


# BasePost와 관련 모델들
class BasePost(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class EventPost(BasePost):
    event_date = models.DateField()

class ReadingGroupPost(BasePost):
    meeting_time = models.DateTimeField()

class ReadingTipPost(BasePost):
    CATEGORY_CHOICES = [
        ('reading', '독서 팁'),
        ('writing', '글쓰기 팁'),
        ('other', '기타'),
    ]
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='reading'
    )
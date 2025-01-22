# File: community/models.py


from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField  # 파일 업로드 지원
from django.contrib.auth import get_user_model

class Book(models.Model):
    # NAVER Book API에서 받아올 수 있는 주요 필드 예시
    title        = models.CharField(max_length=200)
    author       = models.CharField(max_length=100, blank=True, null=True)
    publisher    = models.CharField(max_length=100, blank=True, null=True)
    pubdate      = models.CharField(max_length=20, blank=True, null=True)  # YYYYMMDD 형태가 올 수 있음
    thumbnail_url= models.URLField(blank=True, null=True)
    link         = models.URLField(blank=True, null=True)  # NAVER 도서 링크
    
    def __str__(self):
        return self.title

class PostCategory(models.TextChoices):
    ESSAY   = 'essay',   '에세이'
    POETRY  = 'poetry',  '시'
    NOVEL   = 'novel',   '소설'
    NONLIT  = 'nonlit',  '비문학'


class Post(models.Model):
    title       = models.CharField(max_length=200) 
    content = RichTextUploadingField()  # 파일 업로드가 가능한 CKEditor 필드
    
    # 작성자 (인증기능 추가 전까지는 CharField로 간단히)
    writer      = models.CharField(max_length=50, default='익명')
    
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





User = get_user_model()

class BasePost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class EventPost(BasePost):
    event_date = models.DateField()

class ReadingGroupPost(BasePost):
    meeting_time = models.DateTimeField()

class ReadingTipPost(BasePost):
    category = models.CharField(max_length=50)
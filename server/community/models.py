# File: community/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model             # User 모델을 가져오는 방식 수정
from django.utils.text import slugify
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()                                   # 파일 상단에서 한 번만 정의

#---------------------------------책 모델--------------------------------------------------
class BookGenre(models.Model):              #책에 추가하는 장르 모델
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self.name_changed():
            self.slug = slugify(self.name)
            # 슬러그 중복 방지 로직 추가
            counter = 1
            while BookGenre.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def name_changed(self):
        if not self.pk:
            return True
        orig = BookGenre.objects.get(pk=self.pk)
        return orig.name != self.name

    class Meta:
        verbose_name = '장르'
        verbose_name_plural = '장르'
        ordering = ['name']

#----------------------------------책 모델----------------------------------

class Book(models.Model):
    # ISBN 10자리/13자리 등 다양하게 존재하므로, 13자리 기준 + 여유
    isbn = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True, 
        verbose_name="ISBN"
    )
    title = models.CharField(max_length=200, verbose_name="책 제목")
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name="저자")
    publisher = models.CharField(max_length=100, blank=True, null=True, verbose_name="출판사")

    # YYYYMMDD 형태를 받을 수도 있으므로 문자열로 저장하되,
    # 혹시 필요한 경우 parsing하여 DateField에 저장하는 방식을 추가할 수도 있음.
    pubdate = models.CharField(max_length=20, blank=True, null=True, verbose_name="출판일(문자열)")

    thumbnail_url = models.URLField(blank=True, null=True, verbose_name="썸네일 이미지 URL")
    link = models.URLField(blank=True, null=True, verbose_name="도서 링크")

    # 만약 한 권의 책이 여러 장르에 속할 수 있다면 ManyToManyField 고려
    # 여기서는 단일 장르만 저장한다 가정
    genre = models.ManyToManyField(
        BookGenre, 
        blank=True, 
        verbose_name="장르"
    )

    description = models.TextField(blank=True, null=True, verbose_name="책 설명")

    priority = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name='우선순위',
        help_text='낮은 숫자가 더 높은 우선순위를 가집니다 (예: 1이 2보다 높음).'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="등록일"
    )


    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    # 책 활성화 여부 (품절/절판 등으로 리스트 제외 처리 시 유용)
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")

    # 책 조회수 추가
    views = models.PositiveIntegerField(default=0, verbose_name="조회수")

    class Meta:
        ordering = ['priority', 'title']  # 우선순위 높은(숫자 낮은) 책부터 정렬 후, 제목 순
        verbose_name = "책"
        verbose_name_plural = "책 목록"

    def __str__(self):
        return f"[{self.isbn}] {self.title}" if self.isbn else self.title

    def deactivate(self):
        """
        책을 비활성화할 때 사용하는 예시 메소드 (품절/절판 처리 등).
        """
        self.is_active = False
        self.save()

    def increase_views(self):
        """조회수 증가 메소드"""
        self.views += 1
        self.save()

#------------------------------ Post 공통 관리 모델--------------------------------------------------

class PostManager(models.Manager):
    """
    기본적으로 is_deleted=False, is_active=True만 필터링하여 제공.
    필요한 경우 별도 매니저나 커스텀 메소드로 확장 가능.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)

    def get_sidebar_posts(self):
        return (self.get_queryset()
                .filter(is_side_bar=True)
                .select_related('writer', 'book')              # N+1 문제 해결
                .prefetch_related('tags')                      # N+1 문제 해결
                .order_by('-updated_at'))

    def get_active_events(self):                              # 활성 이벤트 조회 메서드 추가
        return self.get_queryset().filter(
            event_date__gte=timezone.now().date()
        ).order_by('event_date')


class PostCategory(models.TextChoices):
    BOOK_POST           = 'book_post', '책 게시글'
    READING_GROUP_POST  = 'reading_group_post', '독서 모임'
    BOOK_REVIEW_EVENT   = 'book_review_event', '서평 이벤트'
    BOOK_TALK_POST      = 'book_talk_post', '북토크'
    PERSONAL_EVENT_POST = 'personal_event_post', '개인 이벤트'





class PostTag(models.Model):      
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self.name_changed():
            self.slug = slugify(self.name)
            counter = 1
            while PostTag.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def name_changed(self):
        if not self.pk:
            return True
        orig = PostTag.objects.get(pk=self.pk)
        return orig.name != self.name

    class Meta:
        verbose_name = '태그'
        verbose_name_plural = '태그'
        ordering = ['name']


class PostImage(models.Model):
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True,  # null 허용으로 변경
        blank=True  # blank 허용으로 변경
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)  # null 허용으로 변경
    post = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(
        upload_to='post_images/%Y/%m/%d/',
        verbose_name="이미지"
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "게시글 이미지"
        verbose_name_plural = "게시글 이미지 목록"


#-------------------------------Post 모델---------------------------------------------------------------------------


class Post(models.Model):
    """
    기존 BasePost + Post 모델의 공통 필드를 모두 통합한 추상 모델.
    하위 모델들이 이 클래스를 상속받아 사용한다.
    게시글에는 우선순위 모델이 필요없다.
    대신 사이드바에 노출 여부를 표시하는 필드와 고정 여부를 추가한다.

    """
    # 공통 필드
    title       = models.CharField(max_length=200, verbose_name="제목")
    content     = models.TextField(verbose_name="내용")
    writer      = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    views       = models.PositiveIntegerField(default=0, verbose_name="조회수")

    # 날짜/시간
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name="등록일")
    updated_at  = models.DateTimeField(auto_now=True, verbose_name="수정일")

    # 상태/제어 플래그
    is_active   = models.BooleanField(default=True, verbose_name="활성화 여부")
    is_pinned   = models.BooleanField(default=False, verbose_name="고정 여부")
    is_deleted  = models.BooleanField(default=False, verbose_name="삭제 여부")
    is_side_bar = models.BooleanField(
        default=False, 
        verbose_name="사이드바 노출 여부",
        help_text="게시글을 사이드바에 표시할지 여부를 설정합니다."
    )

    # 검색을 위한 벡터 필드 추가
    search_vector = SearchVectorField(null=True)                # 검색 기능 추가

    # 카테고리
    category = models.CharField(
        max_length=50,
        choices=PostCategory.choices,  # 선택 항목 직접 연결
        default=PostCategory.BOOK_POST,
        verbose_name="카테고리",
        help_text="게시글 유형 선택"
    )

    # 예) 태그(M2M)
    tags        = models.ManyToManyField('PostTag', blank=True, verbose_name="태그")

    # 예) 책 관련 글이면 연결 (null/blank 허용)
    book        = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="책"
    )

    # 커스텀 매니저 교체
    objects = PostManager()

    class Meta:
        abstract = True
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            GinIndex(fields=['search_vector'])                 # 검색 성능 향상을 위한 인덱스
        ]

    def soft_delete(self):
        """실제 삭제 대신 is_deleted=True로 설정해 논리삭제."""
        self.is_deleted = True
        self.save()

    def increase_views(self):
        """조회수 증가 메소드"""
        self.views += 1
        self.save()

    def save(self, *args, **kwargs):
        # 삭제된 게시물은 사이드바에 표시하지 않음
        if self.is_deleted:
            self.is_side_bar = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    



# -------------------- Post 하위 모델들 (개별적으로 확장) ----------------------


#----------------------------------일반 게시글 모델----------------------------------
class GeneralPost(Post):
    """
    일반 게시글에 해당. 추가 필드가 없으면 그대로 사용 가능.
    필요하면 extra 필드를 정의하세요.
    """
    class Meta(Post.Meta):
        verbose_name = "일반 게시글"
        verbose_name_plural = "일반 게시글 목록"




#----------------------------------독서 그룹 모델----------------------------------


class ReadingGroupPost(Post):
    """
    base.html(사이드바)에 노출할 로직이 필요하다면, Manager 또는 View단에서
    이 모델을 필터링하여 템플릿에 전달.
    """
    event_date = models.DateField(
        null=True,  # null 허용으로 변경
        blank=True  # blank 허용으로 변경
    )

    def save(self, *args, **kwargs):
        self.is_side_bar = True                             # save() 메서드에서 처리
        super().save(*args, **kwargs)

    def is_event_upcoming(self):
        return self.event_date >= timezone.now().date()
    
    class Meta(Post.Meta):
        verbose_name = "독서 모임 게시글"
        verbose_name_plural = "독서 모임 게시글 목록"

    

   
    





#----------------------------------독서 팁 모델----------------------------------
class ReadingTipPost(Post):
    """
    독서 팁, 글쓰기 팁 등
    """
    TIP_CATEGORY_CHOICES = [
        ('reading', '독서 팁'),
        ('writing', '글쓰기 팁'),
        ('other', '기타'),
    ]
    tip_category = models.CharField(
        max_length=50,
        choices=TIP_CATEGORY_CHOICES,
        default='reading'
    )

    class Meta(Post.Meta):
        verbose_name = "독서 팁 게시글"
        verbose_name_plural = "독서 팁 게시글 목록"

    def save(self, *args, **kwargs):
        self.is_side_bar = True                             # save() 메서드에서 처리
        super().save(*args, **kwargs)




#----------------------------------책 이벤트 모델----------------------------------
class BookEventPost(Post):
    event_start_date = models.DateTimeField(
        null=True,  # null 허용으로 변경
        blank=True,  # blank 허용으로 변경
        verbose_name="이벤트 시작일시"
    )
    event_end_date = models.DateTimeField(
        null=True,  # null 허용으로 변경
        blank=True,  # blank 허용으로 변경
        verbose_name="이벤트 종료일시"
    )

    class Meta:
        verbose_name = "책 이벤트 게시글"
        verbose_name_plural = "책 이벤트 게시글 목록"
        indexes = []  # 부모 클래스의 인덱스 상속 제거

class BookReviewEventPost(BookEventPost):
    class Meta:
        verbose_name = "책 리뷰 이벤트"
        verbose_name_plural = "책 리뷰 이벤트 목록"
        indexes = []

class PersonalBookEventPost(BookEventPost):
    class Meta:
        verbose_name = "개인 책 이벤트"
        verbose_name_plural = "개인 책 이벤트 목록"
        indexes = []

class BookTalkEventPost(BookEventPost):
    class Meta:
        verbose_name = "북토크"
        verbose_name_plural = "북토크 목록"
        indexes = []



#--------------------------------------------------------------------

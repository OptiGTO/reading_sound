# community/views.py (수정된 전체 버전)
import json
from itertools import chain
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, views as auth_views
from django.contrib.auth import login as auth_login
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import requests
from .models import (
    Book, PostImage, GeneralPost, ReadingGroupPost, 
    ReadingTipPost, BookReviewEventPost, BookTalkEventPost,
    PersonalBookEventPost, Comment, Like
)
from .forms import PostForm, CustomUserCreationForm, CustomAuthForm, CommentForm
from .services import search_naver_books
from django.db import models
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.apps import apps
from django import template



#----------------------------------------공통 관련---------------------------------------------------------
# 공통 컨텍스트 생성 함수
def get_common_context(request):
    """동적 컨텍스트 생성 함수"""                                              # 동적 컨텍스트 함수 설명                        
    events_qs = list(chain(                                                 # 이벤트 쿼리셋 체인 시작                         
        BookReviewEventPost.objects.filter(is_active=True),                  # 책 리뷰 이벤트 필터                            
        PersonalBookEventPost.objects.filter(is_active=True),                # 개인 책 이벤트 필터                              
        BookTalkEventPost.objects.filter(is_active=True)                     # 북토크 이벤트 필터                                
    ))                                                                      # 이벤트 쿼리셋 체인 종료                           
    events = sorted(events_qs, key=lambda x: x.event_start_date if x.event_start_date else timezone.now(), reverse=True)  # 이벤트 리스트 정렬                          
    return {                                                                # 컨텍스트 딕셔너리 반환                         
        'site_name': 'reading_sound',                                      # 사이트 이름 설정                                
        'current_user': request.user if request.user.is_authenticated else None,  # 현재 사용자 설정                                
        'sidebar': {                                                       # 사이드바 컨텍스트 설정                           
            'events': events,                                              # 결합 및 정렬된 이벤트 리스트 할당                
            'reading_groups': ReadingGroupPost.objects.filter(is_active=True),   # 독서 모임 필터                                
            'tips': ReadingTipPost.objects.filter(is_active=True),         # 독서 팁 필터                                    
        }
    }


#----------------------------------------게시물 생성 관련---------------------------------------------------------
# 게시물 생성 뷰
def post_view(request):
    """새 게시물 작성 처리"""
    if not request.user.is_authenticated:
        messages.error(request, "로그인이 필요합니다.")
        return redirect('community:login')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                process_and_save_post(request, form)                               # 게시글 저장 프로세스 호출process_and_save_post
                messages.success(request, "게시물이 성공적으로 작성되었습니다.")
                
                # 캐시 관련 헤더 추가 후 리다이렉트
                response = redirect('community:home')
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                return response

            except Exception as e:
                print(f"Error saving post: {e}")
                messages.error(request, "게시물 저장 중 오류가 발생했습니다. 다시 시도해주세요.")
        else:
            print(f"폼 오류: {form.errors}")
            messages.error(request, "입력 형식이 올바르지 않습니다. 다시 확인해주세요.")
    else:
        form = PostForm()
    
    context = {
        'form': form,
        **get_common_context(request)
    }
    
    return render(request, 'community/post.html', context)




# 게시글 저장 프로세스 함수
def process_and_save_post(request, form):
    """게시글과 관련 책, 이미지 데이터를 저장하는 함수"""
    post = form.save(commit=False)
    post.writer = request.user

    # 책 데이터 처리 (일원화된 로직 사용)
    book = process_book_data(request)              # 책 데이터 처리 함수 호출 process_book_data
    if book:
        post.book = book

    post.save()

    # 이미지 파일 저장 처리
    images = request.FILES.getlist('post_images')
    if images:
        for image in images:
            PostImage.objects.create(image=image, post=post)

    return post

# 도서 데이터 처리 함수
def process_book_data(request):
    """사용자가 선택한 도서 정보를 처리하여 Book 객체를 반환"""
    selected_data = request.POST.get('selected_book_data')
    if not selected_data:
        return None

    try:
        book_info = json.loads(selected_data)
    except json.JSONDecodeError:
        return None

    # 한글 장르 값이 넘어올 경우 내부 값으로 변환
    genre_mapping = {
        '에세이': 'essay',
        '소설': 'fiction',
        '비문학': 'non_fiction',
        '과학': 'science',
        '시': 'poetry'
    }
    # book_info에 전달된 장르 값이 한글이면 매핑, 아니면 그대로 사용
    book_info['genre'] = genre_mapping.get(book_info.get('genre', ''), book_info.get('genre', 'essay'))

    defaults = {
        'author': book_info.get('author', ''),
        'publisher': book_info.get('publisher', ''),
        'pubdate': book_info.get('pubdate', ''),
        'thumbnail_url': book_info.get('thumbnail_url', ''),
        'link': book_info.get('link', ''),
        'isbn': book_info.get('isbn', ''),
        'description': book_info.get('description', ''),
        'genre': book_info.get('genre', 'essay')
    }
    
    # 만약 ISBN이 존재한다면 ISBN으로 중복 체크를 강화할 수도 있습니다.
    return Book.objects.get_or_create(
        title=book_info.get('title', ''),
        author=book_info.get('author', ''),
        defaults=defaults
    )[0]



#----------------------------------------메인 페이지 관련---------------------------------------------------------
# 메인 페이지 뷰
def home_view(request):
    """홈페이지 렌더링 - 도서 목록 및 게시물 표시"""
    
    essay_books = Book.objects.filter(genre='essay')
    fiction_books = Book.objects.filter(genre='fiction')
    non_fiction_books = Book.objects.filter(genre='non_fiction')
    science_books = Book.objects.filter(genre='science')
    poetry_books = Book.objects.filter(genre='poetry')
    
    # ContentType 미리 가져오기
    book_content_type = ContentType.objects.get_for_model(Book)
    
    # 각 책의 좋아요 수와 게시글 수를 계산
    for book in chain(essay_books, fiction_books, non_fiction_books, science_books, poetry_books):
        book.likes_count = Like.objects.filter(
            content_type=book_content_type,
            object_id=book.id
        ).count()
        
        book.post_count = (
            book.generalpost_set.count()
            + book.readinggrouppost_set.count()
            + book.readingtippost_set.count()
            + BookReviewEventPost.objects.filter(book=book).count()
            + PersonalBookEventPost.objects.filter(book=book).count()
            + BookTalkEventPost.objects.filter(book=book).count()
        )
    
    context = {
        **get_common_context(request),
        'books': list(chain(essay_books, fiction_books, non_fiction_books, science_books, poetry_books)),
        'essay_books': essay_books,
        'fiction_books': fiction_books,
        'non_fiction_books': non_fiction_books,
        'science_books': science_books,
        'poetry_books': poetry_books,
    }
    
    return render(request, "community/index.html", context)






#책 게시판 뷰
def general_post(request):
    """일반 게시판 페이지 렌더링"""
    posts = GeneralPost.objects.all().order_by('-is_pinned', '-created_at').prefetch_related('tags')  # 고정 게시글 우선, 이후 최근 게시글 정렬
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/general_post.html', context)


# 일반 게시글 상세 페이지 뷰 (일반 게시글: 카테고리 'book_post')
def general_post_detail(request, pk):
    """일반 게시글 상세 페이지 뷰 (댓글 처리 포함)"""
    post = get_object_or_404(GeneralPost, pk=pk)
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "댓글을 작성하려면 로그인해야 합니다.")
            return redirect('community:login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.writer = request.user
            comment.content_object = post
            
            # 부모 댓글이 있는 경우 처리
            parent_id = request.POST.get('parent')
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent
                comment.depth = parent.depth + 1
            
            comment.save()
            messages.success(request, "댓글이 추가되었습니다.")
            return redirect(request.path_info)
    else:
        form = CommentForm()

    # 최상위 댓글만 가져오기 (대댓글은 제외)
    content_type = ContentType.objects.get_for_model(GeneralPost)
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=post.id,
        parent__isnull=True  # 최상위 댓글만 선택
    ).order_by('created_at')

    context = {
        'post': post,
        'comment_form': form,
        'comments': comments,
        **get_common_context(request)
    }
    return render(request, 'community/general_post_detail.html', context)

# 독서 모임 뷰 (수정 버전)
def reading_meeting(request):
    """독서 모임 페이지 렌더링"""
    posts = ReadingGroupPost.objects.all().order_by('-is_pinned', '-created_at').prefetch_related('tags')  # 고정 게시글 우선, 이후 최근 게시글 정렬
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/reading_meeting.html', context)


def reading_meeting_detail(request, pk):
    """일반 게시글 상세 페이지 뷰 (댓글 처리 포함)"""
    post = get_object_or_404(ReadingGroupPost, pk=pk)
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "댓글을 작성하려면 로그인해야 합니다.")
            return redirect('community:login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.writer = request.user
            comment.content_object = post
            
            # 부모 댓글이 있는 경우 처리
            parent_id = request.POST.get('parent')
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent
                comment.depth = parent.depth + 1
            
            comment.save()
            messages.success(request, "댓글이 추가되었습니다.")
            return redirect(request.path_info)
    else:
        form = CommentForm()

    # 최상위 댓글만 가져오기 (대댓글은 제외)
    content_type = ContentType.objects.get_for_model(GeneralPost)
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=post.id,
        parent__isnull=True  # 최상위 댓글만 선택
    ).order_by('created_at')

    context = {
        'post': post,
        'comment_form': form,
        'comments': comments,
        **get_common_context(request)
    }
    return render(request, 'community/reading_meeting_detail.html', context)

# 리뷰 이벤트 뷰 (수정 버전)
def review_event(request):
    """리뷰 이벤트 페이지 렌더링"""
    posts = BookReviewEventPost.objects.all().order_by('-is_pinned', '-created_at').prefetch_related('tags')  # 고정 게시글 우선, 이후 최근 게시글 정렬
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/review_event.html', context)

def review_event_detail(request, pk):
    """리뷰 이벤트 상세 페이지 뷰"""
    post = get_object_or_404(BookReviewEventPost, pk=pk)
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "댓글을 작성하려면 로그인해야 합니다.")
            return redirect('community:login')
        form = CommentForm(request.POST)
        if form.is_valid():                                                               # 폼 유효성 검사 성공 시                                   
            comment = form.save(commit=False)                                             # 댓글 임시 저장                                            
            comment.writer = request.user                                                 # 댓글 작성자 설정                                           
            comment.content_object = post                                                 # 댓글 대상 객체 지정                                        
            comment.save()                                                                # 댓글 데이터베이스 저장                                     
            messages.success(request, "댓글이 추가되었습니다.")                            # 성공 메시지 출력                                          
            return redirect(request.path_info)                                            # 현재 페이지 새로고침                                        
        else:                                                                             # 폼 유효성 검사 실패 시                                   
            messages.error(request, "댓글 입력에 오류가 있습니다.")                       # 오류 메시지 출력                                          
    else:                                                                                 # GET 요청인 경우                                          
        form = CommentForm()                                                              # 빈 댓글 폼 생성                                           
    content_type = ContentType.objects.get_for_model(post)                                # 게시글의 컨텐츠 타입 가져오기                             
    comments = Comment.objects.filter(                                                   # 댓글 목록 조회                                             
        content_type=content_type,                                                       # 콘텐츠 타입 조건                                           
        object_id=post.id,                                                               # 글의 ID 조건                                              
        parent__isnull=True                                                              # 최상위 댓글만 선택                                          
    ).order_by('-created_at')     

    
    context = {
        'post': post,
        'comment_form': form,
        'comments': comments,
        **get_common_context(request)
    }
    return render(request, 'community/review_event_detail.html', context)


# 북토크 뷰 (수정 버전)
def booktalk(request):
    """북토크 페이지 렌더링"""
    posts = BookTalkEventPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 BookTalkPost 사용
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/booktalk.html', context)

def booktalk_detail(request, pk):
    """북토크 상세 페이지 뷰"""
    post = get_object_or_404(BookTalkEventPost, pk=pk)
    if request.method == "POST":                                                          # POST 요청인 경우                                        
        if not request.user.is_authenticated:                                             # 사용자 인증 확인                                          
            messages.error(request, "댓글을 작성하려면 로그인해야 합니다.")                    # 로그인 필요 메시지 전달                                    
            return redirect('community:login')                                            # 로그인 페이지로 리다이렉트                                   
        form = CommentForm(request.POST)                                                  # 댓글 폼 생성                                             
        if form.is_valid():                                                               # 폼 유효성 검사 성공 시                                   
            comment = form.save(commit=False)                                             # 댓글 임시 저장                                            
            comment.writer = request.user                                                 # 댓글 작성자 설정                                           
            comment.content_object = post                                                 # 댓글 대상 객체 지정                                        
            comment.save()                                                                # 댓글 데이터베이스 저장                                     
            messages.success(request, "댓글이 추가되었습니다.")                            # 성공 메시지 출력                                          
            return redirect(request.path_info)                                            # 현재 페이지 새로고침                                        
        else:                                                                             # 폼 유효성 검사 실패 시                                   
            messages.error(request, "댓글 입력에 오류가 있습니다.")                       # 오류 메시지 출력                                          
    else:                                                                                 # GET 요청인 경우                                          
        form = CommentForm()                                                              # 빈 댓글 폼 생성                                           
    content_type = ContentType.objects.get_for_model(post)                                # 게시글의 컨텐츠 타입 가져오기                             
    comments = Comment.objects.filter(                                                   # 댓글 목록 조회                                             
        content_type=content_type,                                                       # 콘텐츠 타입 조건                                           
        object_id=post.id,                                                               # 글의 ID 조건                                              
        parent__isnull=True                                                              # 최상위 댓글만 선택                                          
    ).order_by('-created_at')                                                             # 최신순 정렬                                               
    context = {
        'post': post,                                                                  # 글 객체 전달                                              
        'comment_form': form,                                                          # 댓글 폼 전달                                              
        'comments': comments,                                                          # 댓글 리스트 전달                                            
        **get_common_context(request)                                                   # 공통 컨텍스트 포함                                          
    }
    return render(request, 'community/booktalk_detail.html', context)



# 개인 이벤트 뷰 (수정 버전)
def personal_event(request):
    """개인 이벤트 페이지 렌더링"""
    posts = PersonalBookEventPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 PersonalBookEventPost 사용
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/personal_event.html', context)

def personal_event_detail(request, pk):
    """개인 이벤트 상세 페이지 뷰 (댓글 처리 포함)"""                                   # 상세 페이지와 댓글 기능 포함                         
    post = get_object_or_404(PersonalBookEventPost, pk=pk)                                # 개인 이벤트 포스트 객체 조회                             
    if request.method == "POST":                                                          # POST 요청인 경우                                        
        if not request.user.is_authenticated:                                             # 사용자 인증 확인                                          
            messages.error(request, "댓글을 작성하려면 로그인해야 합니다.")                    # 로그인 필요 메시지 전달                                    
            return redirect('community:login')                                            # 로그인 페이지로 리다이렉트                                   
        form = CommentForm(request.POST)                                                  # 댓글 폼 생성                                             
        if form.is_valid():                                                               # 폼 유효성 검사 성공 시                                   
            comment = form.save(commit=False)                                             # 댓글 임시 저장                                            
            comment.writer = request.user                                                 # 댓글 작성자 설정                                           
            comment.content_object = post                                                 # 댓글 대상 객체 지정                                        
            comment.save()                                                                # 댓글 데이터베이스 저장                                     
            messages.success(request, "댓글이 추가되었습니다.")                            # 성공 메시지 출력                                          
            return redirect(request.path_info)                                            # 현재 페이지 새로고침                                        
        else:                                                                             # 폼 유효성 검사 실패 시                                   
            messages.error(request, "댓글 입력에 오류가 있습니다.")                       # 오류 메시지 출력                                          
    else:                                                                                 # GET 요청인 경우                                          
        form = CommentForm()                                                              # 빈 댓글 폼 생성                                           
    content_type = ContentType.objects.get_for_model(post)                                # 게시글의 컨텐츠 타입 가져오기                             
    comments = Comment.objects.filter(                                                   # 댓글 목록 조회                                             
        content_type=content_type,                                                       # 콘텐츠 타입 조건                                           
        object_id=post.id,                                                               # 글의 ID 조건                                              
        parent__isnull=True                                                              # 최상위 댓글만 선택                                          
    ).order_by('-created_at')                                                             # 최신순 정렬                                               
    context = {
        'post': post,                                                                  # 글 객체 전달                                              
        'comment_form': form,                                                          # 댓글 폼 전달                                              
        'comments': comments,                                                          # 댓글 리스트 전달                                            
        **get_common_context(request)                                                   # 공통 컨텍스트 포함                                          
    }
    return render(request, 'community/personal_event_detail.html', context)             # 템플릿 렌더링                                              

# 도서 추천 뷰 (수정 버전)
def recommend_book(request):
    """도서 추천 페이지 렌더링"""
    books = Book.objects.filter(
        is_recommended=True,
        is_active=True
    ).order_by('priority', '-created_at')
    context = {
        **get_common_context(request),
        "books": books
    }
    return render(request, 'community/recommend_book.html', context)



#프로필 뷰
def profile(request):
    """사용자 프로필 정보를 조회하는 뷰"""                                    # 프로필 뷰 설명
    user = request.user
    if not user.is_authenticated:                                          # 비로그인 사용자 체크
        messages.error(request, "로그인이 필요합니다.")
        return redirect('community:login')
    
    context = get_common_context(request)
    
    # 사용자의 게시물 통계
    post_models = [GeneralPost, ReadingGroupPost, ReadingTipPost,          # 게시물 모델 리스트
                  BookReviewEventPost, BookTalkEventPost, PersonalBookEventPost]
    
    total_posts = 0                                                        # 전체 게시물 수 초기화
    for model in post_models:                                             # 각 모델별 게시물 수 합산
        total_posts += model.objects.filter(writer=user).count()
    
    context.update({
        'post_count': total_posts,                                        # 전체 게시물 수
        'comment_count': Comment.objects.filter(writer=user).count(),     # 댓글 수
        'recent_activities': get_recent_activities(user)                  # 최근 활동 내역
    })
    
    return render(request, 'community/profile.html', context)

def get_recent_activities(user):
    """사용자의 최근 5개 활동을 조회"""                                     # 최근 활동 조회 함수 설명
    activities = []
    
    # 최근 게시물 조회
    post_models = [GeneralPost, ReadingGroupPost, ReadingTipPost,          # 게시물 모델 리스트
                  BookReviewEventPost, BookTalkEventPost, PersonalBookEventPost]
    
    recent_posts = []                                                      # 최근 게시물 리스트 초기화
    for model in post_models:                                             # 각 모델별 최근 게시물 조회
        posts = model.objects.filter(writer=user).order_by('-created_at')[:5]
        for post in posts:
            recent_posts.append({
                'type': 'post',
                'title': post.title,
                'date': post.created_at,
                'link': get_post_detail_url(post)                         # 게시물 상세 페이지 URL
            })
    
    # 최근 댓글 조회
    recent_comments = Comment.objects.filter(writer=user).order_by('-created_at')[:5]
    for comment in recent_comments:
        activities.append({
            'type': 'comment',
            'title': f'댓글: {comment.content[:30]}...' if len(comment.content) > 30 else f'댓글: {comment.content}',
            'date': comment.created_at,
            'link': get_post_detail_url(comment.content_object)           # 댓글이 달린 게시물 URL
        })
    
    # 모든 활동을 날짜순으로 정렬
    activities = sorted(recent_posts + activities, key=lambda x: x['date'], reverse=True)
    
    return activities[:5]                                                 # 최근 5개 활동만 반환

def get_post_detail_url(post):
    """게시물 타입에 따른 상세 페이지 URL 반환"""                           # URL 생성 함수 설명
    if isinstance(post, GeneralPost):
        return reverse('community:general_post_detail', args=[post.id])
    elif isinstance(post, ReadingGroupPost):
        return reverse('community:reading_meeting_detail', args=[post.id])
    elif isinstance(post, BookReviewEventPost):
        return reverse('community:review_event_detail', args=[post.id])
    elif isinstance(post, BookTalkEventPost):
        return reverse('community:booktalk_detail', args=[post.id])
    elif isinstance(post, PersonalBookEventPost):
        return reverse('community:personal_event_detail', args=[post.id])
    return '#'                                                           # 기본 URL



# 공지사항 뷰 (수정 버전)
def notice(request):

    """공지사항 페이지 렌더링"""
    #posts = NoticePost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 NoticePost 사용
    context = {
        **get_common_context(request),
        #"posts": posts
    }
    return render(request, 'community/notice.html', context)




# 파르헤시아 뷰 (수정 버전)
""" 파르헤시아 페이지 렌더링 이후 추가 예정
def parrhesia(request):
    
    context = get_common_context(request)
    return render(request, 'community/parrhesia.html', context)
"""


#----------------------------------------회원가입 관련---------------------------------------------------------


# 회원가입 뷰 (수정 버전)
def signup(request):
    """회원가입 페이지 렌더링"""
    context = get_common_context(request)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('community:home')  # 'home'으로 명시적 리다이렉트
        else:
            # 폼 에러 메시지 추가
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    elif request.user.is_authenticated:                              # 이미 로그인 되어있으면 홈으로 이동(사용자의 마지막 페이지로 이동하는건 나중에 추가해야함.)
        return redirect('community:home')           
    else:
        context['form'] = CustomUserCreationForm()
    
    return render(request, 'community/signup.html', context)


# 비밀번호 찾기 뷰 (수정 버전)
def password_reset(request):
    """비밀번호 찾기 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/password_reset.html', context)


# 로그인 뷰 (수정 버전)
def login_view(request):
    """로그인 페이지 렌더링 및 로그인 처리"""
    context = get_common_context(request)
    
    if request.method == 'POST':
        form = CustomAuthForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('community:home')  # 홈으로 리다이렉트
        else:
            # 폼 에러 메시지 추가
            messages.error(request, "로그인에 실패했습니다. 입력 정보를 확인해주세요.")
    elif request.user.is_authenticated:
        return redirect('community:home')
    else:
        context['form'] = CustomAuthForm()
    
    return render(request, 'community/login.html', context)


#----------------------------------------네이버 API 관련---------------------------------------------------------
# 네이버 책 검색 뷰
def naver_book_json(request):
    query = request.GET.get('query')
    if not query:
        return JsonResponse({'error': '검색어가 필요합니다.'}, status=400)

    headers = {
        'X-Naver-Client-Id': settings.NAVER_CLIENT_ID,
        'X-CSRFToken': request.META.get('HTTP_X_CSRFTOKEN', ''),
        'X-Naver-Client-Secret': settings.NAVER_CLIENT_SECRET,
    }
    
    try:
        response = requests.get(
            f'https://openapi.naver.com/v1/search/book.json',
            headers=headers,
            params={
                'query': query,
                'd_isbn': '1'  # ISBN 정보를 포함하도록 설정                   # ISBN 정보 포함 요청
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # ISBN과 description 정보 처리                                         # 응답 데이터 처리
        if 'items' in data:
            for item in data['items']:
                isbn = item.get('isbn', '')
                if isbn and ' ' in isbn:
                    isbn10, isbn13 = isbn.split(' ')
                    item['isbn'] = isbn13 or isbn10
                item['description'] = item.get('description', '').replace('<b>', '').replace('</b>', '')
        
        return JsonResponse(data)
    except requests.RequestException as e:
        print(f"네이버 API 호출 오류: {str(e)}")
        return JsonResponse({'error': '네이버 API 호출 중 오류가 발생했습니다.'}, status=500)


# 네이버 도서 API 관련 뷰 (수정 버전)
def naver_books(request):
    """네이버 도서 검색 API 연동 핸들러"""
    if request.method == 'GET':
        query = request.GET.get('query', '에세이')
        params = {
            "query": query,
            "display": 8,
            "start": 1,
        }
        return fetch_naver_data(params)
    return JsonResponse({'error': '잘못된 요청입니다'}, status=400)

# 네이버 API 호출 함수
def fetch_naver_data(params):
    """네이버 API 호출 공통 함수"""
    try:
        response = requests.get(
            "https://openapi.naver.com/v1/search/book.json",
            headers={
                "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
                "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
            },
            params=params
        )
        return JsonResponse(
            response.json() if response.status_code == 200 
            else {"error": "API 요청 실패"}, 
            safe=False, 
            status=response.status_code
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

#----------------------------------------관리자 기능 뷰---------------------------------------------------------

# 관리자 기능 뷰 (수정 버전)
@staff_member_required
def book_search_view(request):
    """관리자용 도서 검색 기능"""
    context = get_common_context(request)
    if request.method == "POST":
        if keyword := request.POST.get("keyword", "").strip():
            context.update({
                "results": search_naver_books(keyword),
                "keyword": keyword
            })
        else:
            messages.warning(request, "검색어를 입력해주세요")
    return render(request, "admin/book_search.html", context)

@staff_member_required
def book_add_view(request):
    """관리자용 도서 추가 기능"""
    context = get_common_context(request)
    if request.method == "POST":
        # ISBN을 포함한 모든 필드를 가져오도록 수정
        book_fields = ['title', 'author', 'publisher', 'pubdate', 'thumbnail_url', 'link', 'isbn', 'description']
        book_data = {
            field: request.POST.get(field)
            for field in book_fields
            if request.POST.get(field)
        }
        
        if book_data.get('isbn'):
            duplicate_exists = Book.objects.filter(
            Q(title=book_data['title'], author=book_data['author']) |
            Q(isbn=book_data['isbn'])
            ).exists()
        else:
            duplicate_exists = Book.objects.filter(
            title=book_data['title'], author=book_data['author']
            ).exists()

        if duplicate_exists:
            messages.warning(request, f"이미 존재하는 도서입니다: {book_data['title']}")
        else:
            Book.objects.create(**book_data)
            messages.success(request, f"도서 추가 완료: {book_data['title']}")
            return redirect(reverse('admin:community_book_changelist'))
    return redirect(reverse('admin_books_search'))



#----------------------------------------홈 화면 관련---------------------------------------------------------


# 홈 카드 클릭 시 책별 게시물 조회 뷰
def get_posts_by_book(request):
    """특정 도서와 관련된 게시물 목록을 반환하는 API"""                                          # 도서 관련 게시물 API　　　　　
    isbn = request.GET.get('isbn', '')                                                              # 도서 ISBN 조회　　　　　　　
    try:
        # 도서 검색 조건 개선                                                                       # 도서 검색 조건　　　　　　　
        book = Book.objects.filter(                                                                  # 도서 조회　　　　　　　　　
            models.Q(isbn=isbn) if isbn else models.Q(title=request.GET.get('title', ''))
        ).first()                                                                                   # 첫 번째 도서 조회　　　　　
        
        if not book:
            return JsonResponse({
                'posts': [],
                'message': '해당하는 책을 찾을 수 없습니다.',
                'status': 'no_book'
            }, safe=False)
        
        book.increase_views()  # 도서 조회수 증가                                                     # 도서 조회수 증가　　　　　
    
        posts = []
        post_types = [GeneralPost, ReadingGroupPost, BookReviewEventPost, 
                      BookTalkEventPost, PersonalBookEventPost]                                   # 게시글 모델 리스트　　　　　
        
        for post_type in post_types:                                                                   # 각 게시글 모델 반복　　　　　
            qs = post_type.objects.filter(                                                            # 특정 모델에서 도서 관련 게시글 조회　
                book=book,                                                                            # 요청한 도서　　　　　　　
                is_deleted=False,                                                                     # 삭제되지 않은 게시글　　　
                is_active=True                                                                        # 활성화된 게시글　　　　　
            ).order_by('-created_at')                                                                  # 최신순 정렬　　　　　　　
            for post in qs:                                                                              # 각 게시글에 대해 반복　　　　
                # 게시글에 따른 상세 URL 생성                                                      # 상세 페이지 URL 생성　　　　
                # 상세 URL 생성: 클래스 비교 시 isinstance()를 사용
                try:
                    if isinstance(post, GeneralPost):
                        detail_url = reverse('community:general_post_detail', args=[post.id])
                    elif isinstance(post, ReadingGroupPost):
                        detail_url = reverse('community:reading_meeting_detail', args=[post.id])
                    elif isinstance(post, BookReviewEventPost):
                        detail_url = reverse('community:review_event_detail', args=[post.id])
                    elif isinstance(post, BookTalkEventPost):
                        detail_url = reverse('community:booktalk_detail', args=[post.id])
                    elif isinstance(post, PersonalBookEventPost):
                        detail_url = reverse('community:personal_event_detail', args=[post.id])
                    else:
                        detail_url = ''                                                                     # 기본 URL 빈 문자열　　　　
                except Exception as url_error:
                    print(f"Reverse error for post id {post.id}: {url_error}")
                    detail_url = ''
                
                post_dict = {                                                                              # 게시글 데이터를 딕셔너리로 저장　
                    'id': post.id,                                                                        # 게시글 ID　　　　　　　　　
                    'title': post.title,                                                                  # 게시글 제목　　　　　　　
                    'content': post.content,                                                              # 게시글 내용　　　　　　　
                    'writer__username': post.writer.username,                                             # 작성자 이름　　　　　　　　
                    'created_at': post.created_at,                                                        # 생성일시　　　　　　　　　
                    'detail_url': detail_url,                                                             # 상세 페이지 URL 추가　　　　
                    'likes': post.get_likes_count()                                                                   # 좋아요 수 추가　　　　　　　
                }
                ct = ContentType.objects.get_for_model(post)                                              # 게시글 모델의 ContentType　　
                image_obj = PostImage.objects.filter(                                                      # 관련 이미지 조회　　　　　　　
                    content_type=ct,                                                                        # 게시글 ContentType 기준　　
                    object_id=post.id                                                                       # 게시글 ID 기준　　　　　　　
                ).order_by('order').first()                                                                 # 주문 기준 첫 번째 이미지 선택　
                if image_obj:                                                                               # 이미지가 있을 경우　　　　　
                    post_dict['thumbnail_url'] = image_obj.image.url                                      # 썸네일 URL 추가　　　　　　　
                else:
                    post_dict['thumbnail_url'] = ''                                                       # 이미지 없으면 빈 문자열　　　　
                posts.append(post_dict)                                                                     # 리스트에 게시글 추가　　　　　
        
        # 날짜 직렬화 처리                                                                             # 날짜 포맷 변경　　　　　　　
        for post in posts:
            post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M') if post['created_at'] else '날짜 정보 없음'
        
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        posts = posts[:10]
            
        return JsonResponse({
            'posts': posts,
            'book_title': book.title,
            'book_likes': book.get_likes_count(),         # 도서 좋아요 수 추가　　　　
            'book_id': book.id,               # 도서 ID 추가　　　　　　 　　 
            'status': 'success'
        }, safe=False)
    
    except Exception as e:
        return JsonResponse({
            'error': '게시물을 불러오는 중 오류가 발생했습니다.',
            'status': 'error'
        }, status=500)






# base.html 오른쪽 사이드바 통합 검색 뷰
def search_view(request):
    """통합 검색 뷰"""
    query = request.GET.get('query', '')
    results = {'books': [], 'posts': []}

    if query:
        # 책 검색 (제목 기준)
        results['books'] = Book.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(author__icontains=query) |
            models.Q(publisher__icontains=query)
        )[:5]  # 상위 5개 결과만 표시

        # 게시물 검색 (제목+내용 기준)
        post_models = [GeneralPost, ReadingGroupPost, BookReviewEventPost, 
                      BookTalkEventPost, PersonalBookEventPost, ReadingTipPost]
        
        for model in post_models:
            model_results = model.objects.filter(
                models.Q(title__icontains=query) |
                models.Q(content__icontains=query)
            ).select_related('writer', 'book')[:10]  # 각 모델별 상위 10개
            results['posts'].extend(model_results)

    context = {
        **get_common_context(request),
        'query': query,
        'results': results,
        'result_count': len(results['books']) + len(results['posts'])
    }
    return render(request, 'community/search_results.html', context)


#---------------------------------좋아요 기능-----------------------------------------
# 좋아요 기능 처리 (도서)
@csrf_exempt
def like_book(request):
    """도서 좋아요 토글 뷰"""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
        
        book_id = request.POST.get('book_id')
        if not book_id:
            return JsonResponse({'error': '도서 ID가 제공되지 않았습니다.'}, status=400)
        
        try:
            book = Book.objects.get(pk=book_id)
            content_type = ContentType.objects.get_for_model(book)
            
            # 좋아요 토글
            like, created = Like.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=book.id,
                defaults={'content_object': book}
            )
            
            if not created:  # 이미 좋아요가 있으면 삭제
                like.delete()
                is_liked = False
            else:
                is_liked = True
            
            # 좋아요 수 조회
            likes_count = Like.objects.filter(
                content_type=content_type,
                object_id=book.id
            ).count()
            
            return JsonResponse({
                'success': True,
                'likes': likes_count,  # 실제 좋아요 수 반환
                'is_liked': is_liked
            })
            
        except Book.DoesNotExist:
            return JsonResponse({'error': '도서를 찾을 수 없습니다.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)



# 좋아요 기능 처리 (게시물)
@csrf_exempt
def like_post(request):
    """게시글 좋아요 토글 뷰"""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
        
        post_id = request.POST.get('post_id')
        model_name = request.POST.get('model')
        
        if not post_id or not model_name:
            return JsonResponse({'error': '필수 파라미터가 누락되었습니다.'}, status=400)
        
        try:
            Model = apps.get_model('community', model_name)
            post = Model.objects.get(pk=post_id)
            content_type = ContentType.objects.get_for_model(post)
            
            # 좋아요 토글
            like, created = Like.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=post.id,
                defaults={'content_object': post}
            )
            
            if not created:  # 이미 좋아요가 있으면 삭제
                like.delete()
                is_liked = False
            else:
                is_liked = True
            
            likes_count = post.get_likes_count()
            
            return JsonResponse({
                'success': True,
                'likes': likes_count,
                'is_liked': is_liked
            })
            
        except Model.DoesNotExist:
            return JsonResponse({'error': '게시글을 찾을 수 없습니다.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@require_POST
def comment_create(request, post_pk):
    """댓글 생성 뷰"""
    if not request.user.is_authenticated:
        messages.error(request, "로그인이 필요합니다.")
        return redirect('community:login')
    
    content_type = request.POST.get('content_type')
    model = apps.get_model('community', content_type)
    post = get_object_or_404(model, pk=post_pk)
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.writer = request.user
        comment.content_type = ContentType.objects.get_for_model(post)
        comment.object_id = post.pk
        
        parent_pk = request.POST.get('parent')
        if parent_pk:
            parent = get_object_or_404(Comment, pk=parent_pk)
            comment.parent = parent
            
        comment.save()
        messages.success(request, "댓글이 작성되었습니다.")
        
    return redirect(request.META.get('HTTP_REFERER', 'community:home'))




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
    PersonalBookEventPost, Comment
)
from .forms import PostForm, CustomUserCreationForm, CustomAuthForm, CommentForm
from .services import search_naver_books
from django.db import models
from django.db.models import Q

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
                # 게시글 기본 정보 저장
                post = form.save(commit=False)
                post.writer = request.user

                # 책 정보 처리
                if selected_book_data := request.POST.get('selected_book_data'):
                    try:
                        book_info = json.loads(selected_book_data)
                        book, _ = Book.objects.get_or_create(
                            title=book_info.get('title'),
                            defaults={
                                'author': book_info.get('author', ''),
                                'publisher': book_info.get('publisher', ''),
                                'pubdate': book_info.get('pubdate', ''),
                                'thumbnail_url': book_info.get('thumbnail_url', ''),
                                'link': book_info.get('link', ''),
                                'isbn': book_info.get('isbn', ''),
                                'description': book_info.get('description', '')
                            }
                        )
                        post.book = book
                    except json.JSONDecodeError:
                        pass

                # 게시글 저장
                post.save()
                form.save_m2m()  # 태그 관계 저장

                # 이미지 처리
                if images := request.FILES.getlist('post_images'):
                    for image in images:
                        PostImage.objects.create(image=image, post=post)

                messages.success(request, "게시물이 성공적으로 작성되었습니다.")
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

# 게시물 제출 처리 핸들러
def handle_post_submission(request, form):
    """게시물 저장 로직 처리 및 예외 관리"""
    try:
        post = form.save(commit=False)
        if book_data := process_book_data(request):
            post.book = book_data
        post.save()
        return redirect('community:home')
    except json.JSONDecodeError:
        messages.error(request, "유효하지 않은 도서 데이터 형식입니다")
    except Exception as e:
        messages.error(request, f"게시물 저장 오류: {str(e)}")
    return redirect('community:post')

# 도서 데이터 처리 함수
def process_book_data(request):
    """사용자가 선택한 도서 정보 처리 및 데이터베이스 저장"""
    if selected_data := request.POST.get('selected_book_data'):
        book_info = json.loads(selected_data)
        return Book.objects.get_or_create(
            title=book_info.get('title', ''),
            author=book_info.get('author', ''),
            defaults={k: book_info.get(k, '') for k in [
                'publisher', 'pubdate', 'thumbnail_url', 'link', 'isbn' , 'description'
            ]}
        )[0]
    return None


#----------------------------------------메인 페이지 관련---------------------------------------------------------
# 메인 페이지 뷰
def home_view(request):
    """홈페이지 렌더링 - 도서 목록 및 게시물 표시"""
    books = Book.objects.all()
    for book in books:
        book.post_count = (
            book.generalpost_set.count()
            + book.readinggrouppost_set.count()
            + book.readingtippost_set.count()
            + BookReviewEventPost.objects.filter(book=book).count()
            + PersonalBookEventPost.objects.filter(book=book).count()
            + BookTalkEventPost.objects.filter(book=book).count()
        )
    context = get_common_context(request)
    context.update({'books': books})
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
            comment.save()
            messages.success(request, "댓글이 추가되었습니다.")
            return redirect(request.path_info)
        else:
            messages.error(request, "댓글 입력에 오류가 있습니다.")
    else:
        form = CommentForm()
    content_type = ContentType.objects.get_for_model(GeneralPost)
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=post.id,
        parent__isnull=True
    ).order_by('-created_at')
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
    posts = ReadingGroupPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 ReadingGroupPost 사용
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/reading_meeting.html', context)


def reading_meeting_detail(request, pk):
    """독서 모임 상세 페이지 뷰"""
    post = get_object_or_404(ReadingGroupPost, pk=pk)
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
    return render(request, 'community/reading_meeting_detail.html', context)

# 리뷰 이벤트 뷰 (수정 버전)
def review_event(request):
    """리뷰 이벤트 페이지 렌더링"""
    posts = BookReviewEventPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 BookReviewEventPost 사용
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



# 사용자 콘텐츠 뷰 (수정 버전)
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
    #posts = RecommendBookPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 RecommendBookPost 사용
    context = {
        **get_common_context(request),
        #"posts": posts
    }
    return render(request, 'community/recommend_book.html', context)

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
                if post_type == GeneralPost:                                                             # 일반 게시글　　　　　　　　
                    detail_url = reverse('community:general_post_detail', args=[post.id])
                elif post_type == ReadingGroupPost:                                                      # 독서 모임 게시글　　　　　
                    detail_url = reverse('community:reading_meeting_detail', args=[post.id])
                elif post_type == BookReviewEventPost:                                                     # 리뷰 이벤트 게시글　　　　　
                    detail_url = reverse('community:review_event_detail', args=[post.id])
                elif post_type == BookTalkEventPost:                                                       # 북토크 게시글　　　　　　　
                    detail_url = reverse('community:booktalk_detail', args=[post.id])
                elif post_type == PersonalBookEventPost:                                                   # 개인 이벤트 게시글　　　　
                    detail_url = reverse('community:personal_event_detail', args=[post.id])
                else:
                    detail_url = ''                                                                          # 기본 URL 빈 문자열　　　　
                
                post_dict = {                                                                              # 게시글 데이터를 딕셔너리로 저장　
                    'id': post.id,                                                                        # 게시글 ID　　　　　　　　　
                    'title': post.title,                                                                  # 게시글 제목　　　　　　　　
                    'content': post.content,                                                              # 게시글 내용　　　　　　　　
                    'writer__username': post.writer.username,                                             # 작성자 이름　　　　　　　　
                    'created_at': post.created_at,                                                        # 생성일시　　　　　　　　　
                    'detail_url': detail_url,                                                             # 상세 페이지 URL 추가　　　　
                    'likes': post.likes                                                                   # 좋아요 수 추가　　　　　　　
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
            'book_likes': book.likes,         # 도서 좋아요 수 추가　　　　
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
@csrf_exempt                                                                # 좋아요 기능 처리 (도서)　　　
def like_book(request):
    if request.method == "POST":                                              # POST 메서드 확인　　　　　　
        if not request.user.is_authenticated:                                # 인증된 사용자 확인　　　　　
            return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)    # 로그인 필요 메시지　　　　　　
        book_id = request.POST.get('book_id')                                  # 도서 ID 추출　　　　　　　　　
        if not book_id:
            return JsonResponse({'error': '도서 ID가 제공되지 않았습니다.'}, status=400)  # 도서 ID 누락 메시지　　　　　
        try:
            book = Book.objects.get(pk=book_id)                                # 도서 객체 조회　　　　　　　
            book.likes += 1                                                    # 좋아요 수 증가　　　　　　　
            book.save()                                                        # 도서 객체 저장　　　　　　　
            return JsonResponse({'success': True, 'likes': book.likes})          # 결과 반환　　　　　　　　　
        except Book.DoesNotExist:
            return JsonResponse({'error': '도서를 찾을 수 없습니다.'}, status=404)  # 도서 없음 메시지　　　　　
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)              # 잘못된 요청 메시지　　　　　



# 좋아요 기능 처리 (게시물)
@csrf_exempt                                                                # 좋아요 기능 처리 (게시물)　　
def like_post(request):
    if request.method == "POST":                                              # POST 메서드 확인　　　　　　
        if not request.user.is_authenticated:                                # 인증된 사용자 확인　　　　　
            return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)    # 로그인 필요 메시지　　　　　　
        post_id = request.POST.get('post_id')                                  # 게시물 ID 추출　　　　　　　　　
        model_name = request.POST.get('model')                                 # 모델명(게시글 유형) 추출　　　　
        if not post_id or not model_name:
            return JsonResponse({'error': '게시물 ID와 모델명이 제공되지 않았습니다.'}, status=400)  # 필수 파라미터 누락 메시지　
        try:
            from django.apps import apps                                   # 앱 모델 가져오기　　　　　　　
            Model = apps.get_model('community', model_name)                      # 모델 객체 얻기　　　　　　　
            post = Model.objects.get(pk=post_id)                               # 게시물 객체 조회　　　　　　　
            post.likes += 1                                                    # 좋아요 수 증가　　　　　　　
            post.save()                                                        # 게시물 객체 저장　　　　　　　
            return JsonResponse({'success': True, 'likes': post.likes})          # 결과 반환　　　　　　　　　
        except Model.DoesNotExist:
            return JsonResponse({'error': '게시글을 찾을 수 없습니다.'}, status=404)  # 게시글 없음 메시지　　　　　
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)              # 잘못된 요청 메시지　　　　　


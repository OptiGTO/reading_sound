# community/views.py (수정된 전체 버전)
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, views as auth_views
from django.contrib.auth import login as auth_login
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
import requests
from .models import (
    Book, PostImage, GeneralPost, ReadingGroupPost, 
    ReadingTipPost, BookReviewEventPost, BookTalkEventPost,
    PersonalBookEventPost, BookEventPost,
    Post
)
from .forms import PostForm, CustomUserCreationForm, CustomAuthForm
from .services import search_naver_books
from django.db import models

#----------------------------------------공통 관련---------------------------------------------------------
# 공통 컨텍스트 생성 함수
def get_common_context(request):
    """동적 컨텍스트 생성 함수"""
    return {
        'site_name': 'reading_sound',
        'current_user': request.user if request.user.is_authenticated else None,
        'sidebar': {
            'events': BookEventPost.objects.filter(is_active=True),
            'reading_groups': ReadingGroupPost.objects.filter(is_active=True),
            'tips': ReadingTipPost.objects.filter(is_active=True),
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
                                'link': book_info.get('link', '')
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
                        PostImage.objects.create(post=post, image=image)

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
                'publisher', 'pubdate', 'thumbnail_url', 'link', 'isbn'
            ]}
        )[0]
    return None


#----------------------------------------메인 페이지 관련---------------------------------------------------------
# 메인 페이지 뷰
def home_view(request):
    """홈페이지 렌더링 - 도서 목록 및 게시물 표시"""
    base_context = get_common_context(request)
    
    context = {
        **base_context,
        "books": Book.objects.all(),
    }
    return render(request, "community/index.html", context)


#책 게시판 뷰
def general_post(request):
    """일반 게시판 페이지 렌더링"""
    posts = GeneralPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 GeneralPost 사용
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/general_post.html', context)

# 독서 모임 뷰 (수정 버전)
def reading_meeting(request):
    """독서 모임 페이지 렌더링"""
    posts = ReadingGroupPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 ReadingGroupPost 사용
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/reading_meeting.html', context)

# 리뷰 이벤트 뷰 (수정 버전)
def review_event(request):
    """리뷰 이벤트 페이지 렌더링"""
    posts = BookReviewEventPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 BookReviewEventPost 사용
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/review_event.html', context)

# 북토크 뷰 (수정 버전)
def booktalk(request):
    """북토크 페이지 렌더링"""
    posts = BookTalkEventPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 BookTalkPost 사용
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/booktalk.html', context)

# 사용자 콘텐츠 뷰 (수정 버전)
def personal_event(request):
    """개인 이벤트 페이지 렌더링"""
    posts = PersonalBookEventPost.objects.all().order_by('-created_at').prefetch_related('tags')  # Post 대신 PersonalBookEventPost 사용
    context = {
        **get_common_context(request),
        "posts": posts
    }
    return render(request, 'community/personal_event.html', context)




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



#----------------------------------------네이버 API 관련---------------------------------------------------------

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
        
        if Book.objects.filter(
            models.Q(title=book_data['title'], author=book_data['author']) |
            (models.Q(isbn=book_data.get('isbn')) if book_data.get('isbn') else models.Q())
        ).exists():
            messages.warning(request, f"이미 존재하는 도서입니다: {book_data['title']}")
        else:
            Book.objects.create(**book_data)
            messages.success(request, f"도서 추가 완료: {book_data['title']}")
            return redirect(reverse('admin:community_book_changelist'))
    return redirect(reverse('admin_books_search'))






# 책별 게시물 조회 뷰

def get_posts_by_book(request):
    """특정 도서와 관련된 게시물 목록을 반환하는 API"""
    isbn = request.GET.get('isbn', '')
    try:
        # 도서 검색 조건 개선
        book = Book.objects.filter(
            models.Q(isbn=isbn) if isbn else models.Q(title=request.GET.get('title', ''))
        ).first()
        
        if not book:
            return JsonResponse({
                'posts': [],
                'message': '해당하는 책을 찾을 수 없습니다.',
                'status': 'no_book'
            }, safe=False)

        posts = []
        post_types = [GeneralPost, ReadingGroupPost, BookReviewEventPost, 
                     BookTalkEventPost, PersonalBookEventPost]
        
        for post_type in post_types:
            posts.extend(
                list(post_type.objects.filter(                                    # list() 변환 추가
                    book=book,
                    is_deleted=False,
                    is_active=True
                ).values(
                    'id',                                                         # id 필드 추가
                    'title', 
                    'content', 
                    'writer__username',
                    'created_at'
                ))
            )
        
        # 날짜 직렬화 처리
        for post in posts:
            post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M') if post['created_at'] else '날짜 정보 없음'

        posts.sort(key=lambda x: x['created_at'], reverse=True)
        posts = posts[:10]
            
        return JsonResponse({
            'posts': posts,
            'book_title': book.title,
            'status': 'success'
        }, safe=False)

    except Exception as e:
        return JsonResponse({
            'error': '게시물을 불러오는 중 오류가 발생했습니다.',
            'status': 'error'
        }, status=500)

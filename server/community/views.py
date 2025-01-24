# community/views.py
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from .models import Book, Post, EventPost, ReadingGroupPost, ReadingTipPost
from .forms import PostForm
from .services import search_naver_books

# 공통 컨텍스트 생성 함수
def get_common_context():
    """여러 뷰에서 공통으로 사용할 컨텍스트 데이터 생성"""
    return {
        'events': EventPost.objects.filter(is_active=True),
        'reading_groups': ReadingGroupPost.objects.filter(is_active=True),
        'tips': ReadingTipPost.objects.filter(is_active=True),
    }

# 메인 페이지 뷰
def home_view(request):
    """홈페이지 렌더링 - 도서 목록 및 게시물 표시"""
    context = {
        "books": Book.objects.all(),
        "posts": Post.objects.all().order_by('-created_at')
    }
    context.update(get_common_context())
    return render(request, "community/index.html", context)

# 게시물 생성 뷰
def post_view(request):
    """새 게시물 작성 처리"""
    context = get_common_context()
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_post_submission(request, form)
    
    return render(request, 'community/post.html', {'form': PostForm(), **context})

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
                'publisher', 'pubdate', 'thumbnail_url', 'link'
            ]}
        )[0]
    return None

# 콘텐츠 페이지 공통 뷰
def login_view(request):
    """로그인 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/login.html', context)

def reading_meeting(request):
    """독서 모임 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/reading_meeting.html', context)

def review_event(request):
    """리뷰 이벤트 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/review_event.html', context)

def booktalk(request):
    """북토크 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/booktalk.html', context)

def your_content(request):
    """사용자 콘텐츠 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/your_content.html', context)

def parrhesia(request):
    """파르헤시아 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/parrhesia.html', context)

def book_sound(request):
    """북사운드 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/book_sound.html', context)

def recommend_book(request):
    """도서 추천 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/recommend_book.html', context)

def notice(request):
    """공지사항 페이지 렌더링"""
    context = get_common_context()
    return render(request, 'community/notice.html', context)

# 네이버 도서 API 관련 뷰
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

# 관리자 기능 뷰
@staff_member_required
def book_search_view(request):
    """관리자용 도서 검색 기능"""
    context = {}
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
    if request.method == "POST":
        book_data = {
            field: request.POST.get(field) 
            for field in Book._meta.get_all_field_names() 
            if field in request.POST
        }
        
        if Book.objects.filter(
            title=book_data['title'], 
            author=book_data['author']
        ).exists():
            messages.warning(request, f"이미 존재하는 도서입니다: {book_data['title']}")
        else:
            Book.objects.create(**book_data)
            messages.success(request, f"도서 추가 완료: {book_data['title']}")
            return redirect(reverse('admin:community_book_changelist'))
    return redirect(reverse('admin_books_search'))
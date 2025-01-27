# community/views.py (수정된 전체 버전)
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from .models import Book, Post, EventPost, ReadingGroupPost, ReadingTipPost
from .forms import PostForm, CustomUserCreationForm, CustomAuthForm
from .services import search_naver_books
from django.contrib.auth import views as auth_views
from django.contrib.auth import login as auth_login

# 공통 컨텍스트 생성 함수
def get_common_context(request):
    """동적 컨텍스트 생성 함수"""
    return {
        'site_name': 'reading_sound',
        'current_user': request.user if request.user.is_authenticated else None,
        'sidebar': {
            'events': EventPost.objects.filter(is_active=True),
            'reading_groups': ReadingGroupPost.objects.filter(is_active=True),
            'tips': ReadingTipPost.objects.filter(is_active=True),
        }
    }

# 메인 페이지 뷰
def home_view(request):
    """홈페이지 렌더링 - 도서 목록 및 게시물 표시"""
    base_context = get_common_context(request)
    context = {
        **base_context,
        "books": Book.objects.all(),
        "posts": Post.objects.all().order_by('-created_at')
    }
    return render(request, "community/index.html", context)

# 게시물 생성 뷰
def post_view(request):
    """새 게시물 작성 처리"""
    context = get_common_context(request)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_post_submission(request, form)
        context['form'] = form
    
    if 'form' not in context:
        context['form'] = PostForm()
    
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
                'publisher', 'pubdate', 'thumbnail_url', 'link'
            ]}
        )[0]
    return None



# 독서 모임 뷰 (수정 버전)
def reading_meeting(request):
    """독서 모임 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/reading_meeting.html', context)

# 리뷰 이벤트 뷰 (수정 버전)
def review_event(request):
    """리뷰 이벤트 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/review_event.html', context)

# 북토크 뷰 (수정 버전)
def booktalk(request):
    """북토크 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/booktalk.html', context)

# 사용자 콘텐츠 뷰 (수정 버전)
def your_content(request):
    """사용자 콘텐츠 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/your_content.html', context)

# 파르헤시아 뷰 (수정 버전)
def parrhesia(request):
    """파르헤시아 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/parrhesia.html', context)

# 북사운드 뷰 (수정 버전)
def book_sound(request):
    """북사운드 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/book_sound.html', context)

# 도서 추천 뷰 (수정 버전)
def recommend_book(request):
    """도서 추천 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/recommend_book.html', context)

# 공지사항 뷰 (수정 버전)
def notice(request):
    """공지사항 페이지 렌더링"""
    context = get_common_context(request)
    return render(request, 'community/notice.html', context)

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
        # 모든 필드 이름을 가져오는 방식 수정
        book_data = {
            field.name: request.POST.get(field.name)
            for field in Book._meta.get_fields()
            if field.name in request.POST
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
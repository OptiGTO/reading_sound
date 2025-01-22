#File: community/views.py
import json
from django.shortcuts import render, redirect
from .models import Book, Post, EventPost, ReadingGroupPost, ReadingTipPost
from .forms import PostForm
from django.conf import settings
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def get_common_context():
    return {
        'events': EventPost.objects.filter(is_active=True),
        'reading_groups': ReadingGroupPost.objects.filter(is_active=True),
        'tips': ReadingTipPost.objects.filter(is_active=True),
    }

def home_view(request):
    books = Book.objects.all()
    posts = Post.objects.all().order_by('-created_at')
    context = {"books": books,
               "posts": posts, 
               } 
    context.update(get_common_context())
    return render(request, "community/index.html", context)


def post_view(request):
    context = get_common_context()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # 이미지 업로드 고려 시 request.FILES 필요
        
        if form.is_valid():
            # 1) 먼저 새 글(Post) 객체를 생성 (commit=False)
            post = form.save(commit=False)

            # 2) 사용자가 선택한 책 데이터 처리
            selected_book_data = request.POST.get('selected_book_data', None)
            if selected_book_data:
                book_info = json.loads(selected_book_data)
                
                # 책이 DB에 있는지 확인 (unique 조건은 적절히 조정)
                # 예: title과 author로 찾는다거나, link로 찾는다거나
                # 아래는 가장 단순하게 title + author로 검색한 예시
                title = book_info.get('title', '')
                author = book_info.get('author', '')
                
                book_obj, created = Book.objects.get_or_create(
                    title=title,
                    author=author,
                    defaults={
                        'publisher': book_info.get('publisher', ''),
                        'pubdate': book_info.get('pubdate', ''),
                        'thumbnail_url': book_info.get('thumbnail_url', ''),
                        'link': book_info.get('link', ''),
                    }
                )
                # 새로 생성된 Book 객체를 Post에 연결
                post.book = book_obj

            # 3) Post 객체 최종 저장
            post.save()

            return redirect('community:home')  # 게시 후 홈으로 이동
    else:
        form = PostForm()

    return render(request, 'community/post.html', {'form': form},context)


def login_view(request):
    context = get_common_context()
    # Add login-specific context if needed
    return render(request, 'community/login.html', context)

def reading_meeting(request):
    context = get_common_context()
    # Add reading meeting-specific context
    return render(request, 'community/reading_meeting.html', context)

def review_event(request):
    context = get_common_context()
    # Add review event-specific context
    return render(request, 'community/review_event.html', context)

def booktalk(request):
    context = get_common_context()
    # Add booktalk-specific context
    return render(request, 'community/booktalk.html', context)

def your_content(request):
    context = get_common_context()
    # Add your_content-specific context
    return render(request, 'community/your_content.html', context)

def parrhesia(request):
    context = get_common_context()
    # Add parrhesia-specific context
    return render(request, 'community/parrhesia.html', context)

def book_sound(request):
    context = get_common_context()
    # Add book_sound-specific context
    return render(request, 'community/book_sound.html', context)

def recommend_book(request):
    context = get_common_context()
    # Add recommend_book-specific context
    return render(request, 'community/recommend_book.html', context)

def notice(request):
    context = get_common_context()
    # Add notice-specific context
    return render(request, 'community/notice.html', context)

def naver_book_json(request):
    """
    Example view that calls the Naver Book Search API 
    and returns JSON data to the client.
    """
    # 1) Get query (keyword) from request GET parameters (or hardcode for testing).
    query = request.GET.get('query', '주식')  # Default to '주식' if not provided.

    # 2) Define the endpoint and headers.
    NAVER_API_URL = "https://openapi.naver.com/v1/search/book.json"  # JSON endpoint
    headers = {
        "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
    }

    # 3) Define any additional query parameters (like display, start).
    params = {
        "query": query,
        "display": 10,       # how many results to display per page
        "start": 1,         # which page of results to start
    }

    # 4) Make the request using `requests`.
    response = requests.get(NAVER_API_URL, headers=headers, params=params)

    # 5) Handle potential errors (e.g., 4xx or 5xx from the Naver API).
    if response.status_code != 200:
        return JsonResponse(
            {"error": f"Failed to fetch data from Naver API. Status code: {response.status_code}"},
            status=500
        )

    # 6) Return the JSON response from Naver directly to the client.
    data = response.json()  # The Naver Book Search API will give JSON
    return JsonResponse(data, safe=False)







def naver_book_template(request):      #홈페이지에서 템플릿을 맞춰 책 정보를 출력
    """
    Example view that calls the Naver Book Search API 
    and returns JSON data to the client.
    """
    # 1) Get query (keyword) from request GET parameters (or hardcode for testing).
    query = request.GET.get('query', '주식')  # Default to '주식' if not provided.

    # 2) Define the endpoint and headers.
    NAVER_API_URL = "https://openapi.naver.com/v1/search/book.json"  # JSON endpoint
    headers = {
        "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
    }

    # 3) Define any additional query parameters (like display, start).
    params = {
        "query": query,
        "display": 10,       # how many results to display per page
        "start": 1,         # which page of results to start
    }

    # 4) Make the request using `requests`.
    response = requests.get(NAVER_API_URL, headers=headers, params=params)

    # 5) Handle potential errors (e.g., 4xx or 5xx from the Naver API).
    if response.status_code != 200:
        return JsonResponse(
            {"error": f"Failed to fetch data from Naver API. Status code: {response.status_code}"},
            status=500
        )

    # 6) Return the JSON response from Naver directly to the client.
    data = response.json()  # The Naver Book Search API will give JSON

    search_results = data['items']
    return render(request, 'community/naver_book_template.html', {'search_results': search_results})



@csrf_exempt
def naver_books(request):
    if request.method == 'GET':
        query = request.GET.get('query', '에세이')
        
        NAVER_API_URL = "https://openapi.naver.com/v1/search/book.json"
        headers = {
            "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
        }
        
        params = {
            "query": query,
            "display": 8,
            "start": 1,
        }
        
        try:
            response = requests.get(NAVER_API_URL, headers=headers, params=params)
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({"error": "API 요청 실패"}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)









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
from .services import search_naver_books  # Keep service layer separation

#공용필드
def get_common_context():
    return {
        'events': EventPost.objects.filter(is_active=True),
        'reading_groups': ReadingGroupPost.objects.filter(is_active=True),
        'tips': ReadingTipPost.objects.filter(is_active=True),
    }


def home_view(request):
    context = {
        "books": Book.objects.all(),
        "posts": Post.objects.all().order_by('-created_at')
    }
    context.update(get_common_context())
    return render(request, "community/index.html", context)



def post_view(request):
    context = get_common_context()
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            return handle_post_submission(request, form)
    
    return render(request, 'community/post.html', 
                 {'form': PostForm(), **context})

def handle_post_submission(request, form):
    try:
        post = form.save(commit=False)
        if book_data := process_book_data(request):
            post.book = book_data
        post.save()
        return redirect('community:home')
    except json.JSONDecodeError:
        messages.error(request, "Invalid book data format")
    except Exception as e:
        messages.error(request, f"Error saving post: {str(e)}")
    return redirect('community:post')

def process_book_data(request):
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

# Naver API Views


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





def naver_books(request):
    if request.method == 'GET':
        query = request.GET.get('query', '에세이')
        params = {
            "query": query,
            "display": 8,
            "start": 1,
        }
        return fetch_naver_data(params)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def fetch_naver_data(params):
    try:
        response = requests.get(
            "https://openapi.naver.com/v1/search/book.json",
            headers={
                "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
                "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
            },
            params=params
        )
        return JsonResponse(response.json() if response.status_code == 200 
                          else {"error": "API request failed"}, 
                          safe=False, 
                          status=response.status_code)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# Admin Views
@staff_member_required
def book_search_view(request):
    context = {}
    if request.method == "POST":
        if keyword := request.POST.get("keyword", "").strip():
            context.update({
                "results": search_naver_books(keyword),
                "keyword": keyword
            })
        else:
            messages.warning(request, "Please enter a search term")
    return render(request, "admin/book_search.html", context)

@staff_member_required
def book_add_view(request):
    if request.method == "POST":
        book_data = {field: request.POST.get(field) 
                    for field in Book._meta.get_all_field_names() 
                    if field in request.POST}
        
        if Book.objects.filter(title=book_data['title'], 
                             author=book_data['author']).exists():
            messages.warning(request, f"Book already exists: {book_data['title']}")
        else:
            Book.objects.create(**book_data)
            messages.success(request, f"Book added: {book_data['title']}")
            return redirect(reverse('admin:community_book_changelist'))
    return redirect(reverse('admin_books_search'))




"""----------------------------------------------------------------------------------------------------------------------------------------------"""











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









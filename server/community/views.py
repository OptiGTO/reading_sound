#File: community/views.py

from django.shortcuts import render, redirect
from .models import Book
import requests
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .forms import PostForm



def home_view(request):
    books = Book.objects.all()
    context = {"books": books}
    return render(request, "community/index.html", context)


def post_view(request):
    """
    글쓰기 페이지 (GET) & 글 저장 (POST)
    """
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()  # DB에 저장
            # 저장 후, 예: 홈으로 이동하거나, 방금 작성한 post 상세 페이지로 이동
            return redirect('community:home')
    else:
        form = PostForm()

    return render(request, 'community/post.html', {'form': form})  # 작성할 템플릿 경로

def login_view(request):
    return render(request, 'community/login.html')

def reading_meeting(request):
    return render(request, 'community/reading_meeting.html')

def review_event(request):
    return render(request, 'community/review_event.html')

def booktalk(request):
    return render(request, 'community/booktalk.html')

def your_content(request):
    return render(request, 'community/your_content.html')

def parrhesia(request):
    return render(request, 'community/parrhesia.html')

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









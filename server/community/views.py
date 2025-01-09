#File: community/views.py

from django.shortcuts import render
from .models import Book
import requests
from django.http import JsonResponse
from django.conf import settings



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



def home_view(request):
    # Simple example: fetch all books from DB
    books = Book.objects.all()
    return render(request, 'community/index.html', {'books': books})



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






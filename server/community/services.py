import requests
from django.conf import settings

NAVER_BOOK_API_URL = "https://openapi.naver.com/v1/search/book.json"

def search_naver_books(keyword, display=10):
    """
    네이버 책 API를 사용해 검색한 결과를 리스트 형태로 반환.
    """
    headers = {
        "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
    }
    params = {
        "query": keyword,
        "display": display,
    }
    response = requests.get(NAVER_BOOK_API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])  # items 리스트 반환
    else:
        # 에러 처리(로그 남기기 등)
        return []

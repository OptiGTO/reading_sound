import requests
from django.conf import settings

NAVER_BOOK_API_URL = "https://openapi.naver.com/v1/search/book.json"

def search_naver_books(keyword, display=10):
    """
    네이버 책 API를 사용해 검색한 결과를 리스트 형태로 반환.
    반환되는 데이터에 ISBN과 책 설명(description) 포함
    """
    headers = {
        "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
    }
    params = {
        "query": keyword,
        "display": display,
        "d_isbn": "1"  # ISBN 정보를 포함하도록 설정                           # ISBN 정보 포함 요청
    }
    response = requests.get(NAVER_BOOK_API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        for item in items:
            # ISBN 정보 처리 (ISBN13 우선, 없으면 ISBN10 사용)                 # ISBN13 우선 처리
            isbn = item.get('isbn', '')
            if isbn and ' ' in isbn:
                isbn10, isbn13 = isbn.split(' ')
                item['isbn'] = isbn13 or isbn10
            # description에서 HTML 태그 제거                                    # HTML 태그 제거하여 설명 정보 저장
            item['description'] = item.get('description', '').replace('<b>', '').replace('</b>', '')
        return items
    else:
        # 에러 처리(로그 남기기 등)
        return []

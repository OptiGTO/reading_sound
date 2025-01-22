from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Book
from .services import search_naver_books  

def book_search_view(request):
    """
    Admin 페이지에서 '도서 검색' 폼을 보여주고, 
    검색어가 들어오면 Naver Book API 결과를 표시한다.
    """
    context = {}
    
    if request.method == "POST":
        keyword = request.POST.get("keyword", "").strip()
        if keyword:
            books = search_naver_books(keyword)
            context["results"] = books
            context["keyword"] = keyword
        else:
            messages.warning(request, "검색어를 입력해주세요.")
    
    return render(request, "admin/book_search.html", context)

def book_add_view(request):
    """
    검색 결과 목록 중 하나를 선택 → DB에 저장하기 위한 뷰
    """
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        publisher = request.POST.get("publisher")
        pubdate = request.POST.get("pubdate")
        thumbnail_url = request.POST.get("thumbnail_url")
        link = request.POST.get("link")

        # 혹시 이미 DB에 존재하는지 확인 (제목 + 저자 기준 or 더 정밀한 기준)
        book_exists = Book.objects.filter(title=title, author=author).exists()
        if book_exists:
            messages.warning(request, f"이미 존재하는 책입니다: [{title}]")
            return redirect(reverse('admin_books_search'))
        
        # 새 책 저장
        Book.objects.create(
            title=title,
            author=author,
            publisher=publisher,
            pubdate=pubdate,
            thumbnail_url=thumbnail_url,
            link=link,
        )
        messages.success(request, f"책이 추가되었습니다: [{title}]")
        return redirect(reverse('admin:community_book_changelist'))  
        # admin의 Book 목록 페이지로 리다이렉트
    
    # 잘못된 접근이면 그냥 검색 페이지로 보냄
    return redirect(reverse('admin_books_search'))

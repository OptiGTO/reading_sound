#File: community/urls.py
#
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views




app_name = 'community'

urlpatterns = [
    

    path('naver-books/', views.naver_books, name='naver_books'), # 네이버 책 검색 뷰

    path('post/', views.post_view, name='post'),      # 게시물 뷰
    path('book_sound/', views.book_sound, name='book_sound'),   # 책 소리 뷰
    path('reading_meeting/', views.reading_meeting, name='reading_meeting'),        # 독서 모임 뷰
    path('review_event/', views.review_event, name='review_event'), # 리뷰 이벤트 뷰
    path('booktalk/', views.booktalk, name='booktalk'),     # 북토크 뷰
    path('your_content/', views.your_content, name='your_content'), # 사용자 콘텐츠 뷰
    path('parrhesia/', views.parrhesia, name='parrhesia'),  # 파르헤시아 뷰
    path('recommend_book/', views.recommend_book, name='recommend_book'), # 도서 추천 뷰

    
    path('notice/', views.notice, name='notice'),       # 공지사항 뷰


    path('login/', views.login_view, name='login'),    # 로그인 뷰

    path('logout/', auth_views.LogoutView.as_view(next_page='community:home'), name='logout'),  # 로그아웃 뷰
    path('signup/', views.signup, name='signup'),   # 회원가입 뷰


    path('', views.home_view, name='home'),
]

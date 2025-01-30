#File: community/urls.py
#
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views




app_name = 'community'

urlpatterns = [
    
    
    path('get-posts-by-book/', views.get_posts_by_book, name='get_posts_by_book'), # 책별 게시물 조회 뷰
    path('naver-books/', views.naver_books, name='naver_books'), # 네이버 책 검색 뷰
    path('naver-book-json/', views.naver_book_json, name='naver_book_json'),  # 네이버 책 검색 뷰

    path('post/', views.post_view, name='post'),      # 글쓰기 뷰
    path('general_post/', views.general_post, name='general_post'), # 일반 게시판 뷰
    path('reading_meeting/', views.reading_meeting, name='reading_meeting'),        # 독서 모임 뷰
    path('review_event/', views.review_event, name='review_event'), # 리뷰 이벤트 뷰
    path('booktalk/', views.booktalk, name='booktalk'),     # 북토크 뷰
    path('personal_event/', views.personal_event, name='personal_event'), # 개인 이벤트 뷰
    #path('parrhesia/', views.parrhesia, name='parrhesia'),  # 파르헤시아 뷰
    path('recommend_book/', views.recommend_book, name='recommend_book'), # 도서 추천 뷰

    
    path('notice/', views.notice, name='notice'),       # 공지사항 뷰


    path('login/', views.login_view, name='login'),    # 로그인 뷰
    
    # 비밀번호 재설정 관련 URL 패턴들
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='community/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='community/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='community/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='community:home'), name='logout'),  # 로그아웃 뷰
    path('signup/', views.signup, name='signup'),   # 회원가입 뷰

    


    path('', views.home_view, name='home'),
]

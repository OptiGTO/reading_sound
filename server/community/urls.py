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
    path('general_post/<int:pk>/', views.general_post_detail, name='general_post_detail'), # 일반 게시판 상세 뷰
    path('reading_meeting/', views.reading_meeting, name='reading_meeting'),        # 독서 모임 뷰
    path('reading_meeting/<int:pk>/', views.reading_meeting_detail, name='reading_meeting_detail'), # 독서 모임 상세 뷰
    path('review_event/', views.review_event, name='review_event'), # 리뷰 이벤트 뷰
    path('review_event/<int:pk>/', views.review_event_detail, name='review_event_detail'), # 리뷰 이벤트 상세 뷰
    path('booktalk/', views.booktalk, name='booktalk'),     # 북토크 뷰
    path('booktalk/<int:pk>/', views.booktalk_detail, name='booktalk_detail'), # 북토크 상세 뷰
    path('personal_event/', views.personal_event, name='personal_event'), # 개인 이벤트 뷰
    path('personal_event/<int:pk>/', views.personal_event_detail, name='personal_event_detail'), # 개인 이벤트 상세 뷰
    #path('parrhesia/', views.parrhesia, name='parrhesia'),  # 파르헤시아 뷰
    path('recommend_book/', views.recommend_book, name='recommend_book'), # 도서 추천 뷰
    path('profile/', views.profile, name='profile'), # 프로필 뷰
    
    path('search/', views.search_view, name='search'), # 검색 뷰
    
    path('notice/', views.notice, name='notice'),       # 공지사항 뷰

    #----------------------------------------로그인 관련 뷰----------------------------------------

    path('login/', views.login_view, name='login'),    # 로그인 뷰
    
    # 비밀번호 재설정 관련 URL 패턴들
    path('password_reset/', views.password_reset, name='password_reset'),   # 비밀번호 재설정 뷰
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='community/password_reset_done.html'), 
         name='password_reset_done'),   # 비밀번호 재설정 완료 뷰
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='community/password_reset_confirm.html'), 
         name='password_reset_confirm'),   # 비밀번호 재설정 확인 뷰
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='community/password_reset_complete.html'), 
         name='password_reset_complete'),   # 비밀번호 재설정 완료 뷰
    
    
    path('logout/', auth_views.LogoutView.as_view(next_page='community:home'), name='logout'),  # 로그아웃 뷰
    path('signup/', views.signup, name='signup'),   # 회원가입 뷰
    
    #------------------------------ 좋아요 기능 뷰 --------------------------------
    path('like-book/', views.like_book, name='like_book'),                  # 도서 좋아요 기능 뷰

    path('like-post/', views.like_post, name='like_post'),                  # 게시글 좋아요 기능 뷰

    path('', views.home_view, name='home'),

    path('comment/<int:post_pk>/create/', views.comment_create, name='comment_create'),
]

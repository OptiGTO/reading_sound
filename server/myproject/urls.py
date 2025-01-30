
#File: myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from community.views import book_search_view, book_add_view
from django.conf import settings
from django.conf.urls.static import static
from community import views as community_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/books/search/', book_search_view, name='admin_books_search'),
    path('admin/books/add/', book_add_view, name='admin_books_add'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('community/', include('community.urls')),
    path('', include('community.urls')),  # route to the community app
]


# 만약 배포환경으로 바꾼다면, 아래 코드를 수정해야 합니다.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
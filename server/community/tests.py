from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Book, ReadingGroupPost, PostTag




User = get_user_model()

#나중에 프로젝트의 규모가 더 커졌을 때 테스트 코드를 추가해야 함


class ReadingGroupTests(TestCase):
    def setUp(self):
        """테스트에 필요한 기본 데이터 설정"""
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # 테스트용 책 생성
        self.book = Book.objects.create(
            title='테스트 도서',
            author='테스트 작가',
            publisher='테스트 출판사',
            isbn='9791234567890'
        )
        
        # 테스트용 태그 생성
        self.tag = PostTag.objects.create(
            name='테스트태그'
        )
        
        # 테스트용 독서 모임 게시글 생성
        self.reading_group = ReadingGroupPost.objects.create(
            title='테스트 독서 모임',
            content='테스트 독서 모임 내용입니다.',
            writer=self.user,
            book=self.book,
            event_date=timezone.now().date(),
            category='reading_group_post'
        )
        self.reading_group.tags.add(self.tag)
        
        # 테스트 클라이언트 설정
        self.client = Client()

    def test_reading_meeting_view(self):
        """독서 모임 페이지 뷰 테스트"""
        # 페이지 접근 테스트
        response = self.client.get(reverse('community:reading_meeting'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community/reading_meeting.html')
        
        # 컨텍스트 데이터 테스트
        self.assertIn('posts', response.context)
        self.assertTrue(len(response.context['posts']) > 0)
        
        # 첫 번째 게시글 내용 확인
        first_post = response.context['posts'][0]
        self.assertEqual(first_post.title, '테스트 독서 모임')
        self.assertEqual(first_post.writer, self.user)
        self.assertEqual(first_post.book, self.book)
        self.assertTrue(first_post.tags.filter(name='테스트태그').exists())

    def test_reading_group_creation(self):
        """독서 모임 게시글 생성 테스트"""
        self.client.login(username='testuser', password='testpass123')
        
        # 새 독서 모임 게시글 데이터
        new_post_data = {
            'title': '새로운 독서 모임',
            'content': '새로운 독서 모임 내용입니다.',
            'book': self.book.id,
            'event_date': timezone.now().date(),
            'category': 'reading_group_post',
            'tags': [self.tag.id]
        }
        
        # 게시글 생성 요청 - URL 경로 수정
        response = self.client.post(
            reverse('community:create_reading_group'),
            new_post_data,
            follow=True
        )
        
        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, 200)
        
        # 게시글이 성공적으로 생성되었는지 확인
        self.assertTrue(
            ReadingGroupPost.objects.filter(
                title='새로운 독서 모임',
                category='reading_group_post'
            ).exists()
        )

    def test_reading_group_category_filter(self):
        """카테고리 필터링 테스트"""
        # 독서 모임 게시글 생성 (카테고리 명시)
        reading_group_post = ReadingGroupPost.objects.create(
            title='독서 모임 게시글',
            content='독서 모임 게시글 내용',
            writer=self.user,
            book=self.book,
            category='reading_group_post'
        )
        
        # 일반 게시글 생성
        general_post = ReadingGroupPost.objects.create(
            title='일반 게시글',
            content='일반 게시글 내용',
            writer=self.user,
            book=self.book,
            category='book_post'
        )
        
        # 독서 모임 페이지 접근
        response = self.client.get(reverse('community:reading_meeting'))
        
        # 독서 모임 카테고리의 게시글만 표시되는지 확인
        posts = response.context['posts']
        for post in posts:
            self.assertEqual(post.category, 'reading_group_post')
            
        # 일반 게시글이 포함되지 않았는지 확인
        self.assertNotIn(general_post, posts)
        # 독서 모임 게시글이 포함되었는지 확인
        self.assertIn(reading_group_post, posts)

    def test_reading_group_event_date(self):
        """이벤트 날짜 표시 테스트"""
        response = self.client.get(reverse('community:reading_meeting'))
        first_post = response.context['posts'][0]
        
        # 이벤트 날짜가 있는지 확인
        self.assertIsNotNone(first_post.event_date)
        
        # 템플릿에서 날짜가 올바르게 표시되는지 확인
        self.assertContains(response, first_post.event_date.strftime('%Y-%m-%d'))

    def tearDown(self):
        """테스트 데이터 정리"""
        User.objects.all().delete()
        Book.objects.all().delete()
        PostTag.objects.all().delete()
        ReadingGroupPost.objects.all().delete()

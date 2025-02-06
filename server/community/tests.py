from django.test                import TestCase, Client                                    # 테스트 모듈 임포트                                   # 테스트 모듈 임포트                     
from django.urls                import reverse                                             # URL 역참조 모듈 임포트                              # URL 역참조 모듈 임포트                    
from django.contrib.auth        import get_user_model                                      # 사용자 모델 가져오기                               # 사용자 모델 가져오기                     
import json                                                                   # JSON 모듈 임포트                                   # JSON 모듈 임포트                         

# community/models.py 에 정의된 모델들을 임포트 (필요에 따라 수정)                          
from .models                    import Book, GeneralPost                                   # 도서, 일반 게시글 모델 임포트                       # 도서, 일반 게시글 모델 임포트            

#---------------------------------------------------------------------------
# 계정 생성 로직 테스트 클래스
#---------------------------------------------------------------------------
class AccountCreationTest(TestCase):
    def setUp(self):                                                                   # 테스트 전 초기 설정                      # 테스트 전 초기 설정                     
        self.client = Client()                                                       # 테스트 클라이언트 생성            # 테스트 클라이언트 생성          

    def test_signup(self):                                                             # 회원가입 테스트 메서드               # 회원가입 테스트 메서드                
        signup_url = reverse('community:signup')                                     # 회원가입 URL 역참조                 # 회원가입 URL 역참조                  
        data = {                                                                    # 테스트용 회원가입 데이터 생성       # 테스트용 회원가입 데이터 생성        
            'username': 'testuser',                                                  # 사용자 이름                        # 사용자 이름                         
            'email': 'test@example.com',                                             # 이메일 주소                        # 이메일 주소                         
            'password1': 'StrongPassword123',                                        # 비밀번호 입력                      # 비밀번호 입력                        
            'password2': 'StrongPassword123'                                         # 비밀번호 확인                      # 비밀번호 확인                        
        }
        response = self.client.post(signup_url, data)                                # 회원가입 POST 요청                  # 회원가입 POST 요청                   
        User = get_user_model()                                                      # 사용자 모델 가져오기              # 사용자 모델 가져오기                  
        user_exists = User.objects.filter(username='testuser').exists()              # 생성된 사용자 존재 여부 확인       # 생성된 사용자 존재 여부 확인           
        self.assertTrue(user_exists)                                                  # 사용자 생성 확인                    # 사용자 생성 확인                     
        # 회원가입 후 'community:home'로 리디렉션 된다고 가정 (필요 시 수정)                
        self.assertRedirects(response, reverse('community:home'))                    # 리디렉션 확인                         # 리디렉션 확인                          

#---------------------------------------------------------------------------
# 게시물 생성 로직 테스트 클래스
#---------------------------------------------------------------------------
class PostCreationTest(TestCase):
    def setUp(self):
        self.client = Client()                                                      # 테스트 클라이언트 생성                  # 테스트 클라이언트 생성               
        User = get_user_model()                                                     # 사용자 모델 가져오기                    # 사용자 모델 가져오기                
        self.user = User.objects.create_user(username='postuser',                    # 테스트용 사용자 생성                   # 테스트용 사용자 생성               
                                                     password='TestPassword123')           
        self.client.login(username='postuser', password='TestPassword123')            # 테스트 사용자 로그인                    # 테스트 사용자 로그인                 
        # 게시물 생성 시 선택할 도서 정보 준비                                          
        self.book_data = {                                                           # 게시물 생성 시 선택할 도서 정보 준비       # 게시물 생성 시 선택할 도서 정보 준비     
            'title': '테스트 도서',                                                 # 도서 제목                              # 도서 제목                          
            'author': '테스트 저자',                                                # 도서 저자                              # 도서 저자                          
            'publisher': '테스트 출판사',                                           # 출판사 정보                            # 출판사 정보                        
            'pubdate': '2020',                                                      # 출판일 정보                            # 출판일 정보                        
            'thumbnail_url': 'http://example.com/thumbnail.jpg',                    # 썸네일 URL                            # 썸네일 URL                        
            'link': 'http://example.com/book',                                      # 도서 링크                              # 도서 링크                          
            'isbn': '1234567890',                                                   # ISBN 번호                              # ISBN 번호                          
            'description': '테스트 설명'                                            # 도서 설명                              # 도서 설명                          
        }

    def test_create_post(self):
        post_url = reverse('community:post')                                      # 게시물 생성 URL 역참조                 # 게시물 생성 URL 역참조                
        selected_book_data = json.dumps(self.book_data)                           # 도서 정보를 JSON 문자열로 변환           # 도서 정보를 JSON 문자열로 변환          
        data = {
            'title': '테스트 게시물',                                             # 게시물 제목                              # 게시물 제목                          
            'content': '이것은 테스트 게시물 내용입니다.',                          # 게시물 내용                              # 게시물 내용                          
            'category': 'book_post',                                           # 카테고리 (올바른 선택값 사용)             # 카테고리 (올바른 선택값 사용)           
            'selected_book_data': selected_book_data,                              # 선택된 도서 데이터                      # 선택된 도서 데이터                  
            'tags': '테스트, 게시물'                                                # 태그 정보                               # 태그 정보                           
        }
        response = self.client.post(post_url, data, follow=True)                   # 게시물 생성 POST 요청 (리디렉션 따름)       # 게시물 생성 POST 요청 (리디렉션 따름)   
        
        # 디버깅: 응답 상태 코드와 본문 출력                                                             # 디버깅: 응답 상태 코드와 본문 출력               
        print("응답 상태 코드:", response.status_code)                                                 # 응답 상태 코드 출력                           # 응답 상태 코드 출력                                
        print("응답 본문:", response.content.decode())                                                # 응답 본문 출력                                # 응답 본문 출력                                    
        
        self.assertEqual(response.status_code, 200)                                # 응답 상태 코드 200 확인                  # 응답 상태 코드 200 확인             
        post_exists = GeneralPost.objects.filter(title='테스트 게시물').exists()    # 게시물 생성 여부 확인                    # 게시물 생성 여부 확인               
        self.assertTrue(post_exists)                                               # 게시물 생성 확인                         # 게시물 생성 확인                    

#---------------------------------------------------------------------------
# 카드 추가 로직 (도서 카드 관련) 테스트 클래스
#---------------------------------------------------------------------------
class CardAdditionLogicTest(TestCase):
    def setUp(self):
        self.client = Client()                                                      # 테스트 클라이언트 생성             # 테스트 클라이언트 생성              
        self.book = Book.objects.create(                                           # 테스트용 Book 객체 생성 (카드에 표시될 도서 정보)   # 테스트용 Book 객체 생성 (카드에 표시될 도서 정보)
            title='카드 테스트 도서',                                               # 도서 제목                          # 도서 제목                          
            author='테스트 저자',                                                  # 도서 저자                          # 도서 저자                          
            publisher='테스트 출판사',                                             # 출판사 정보                        # 출판사 정보                        
            pubdate='2021',                                                        # 출판일 정보                        # 출판일 정보                        
            thumbnail_url='http://example.com/card.jpg',                         # 썸네일 URL                        # 썸네일 URL                        
            link='http://example.com/bookcard',                                  # 도서 링크                          # 도서 링크                          
            isbn='9876543210',                                                     # ISBN 번호                          # ISBN 번호                          
            description='카드 추가 테스트'                                           # 도서 설명                          # 도서 설명                          
        )
        User = get_user_model()                                                     # 사용자 모델 가져오기               # 사용자 모델 가져오기                
        dummy_user = User.objects.create_user(username='cardtestuser',               # 임시 사용자 생성                   # 임시 사용자 생성                   
                                                     password='TestPass123')            
        self.post = GeneralPost.objects.create(                                    # 해당 도서와 연결된 GeneralPost 객체 생성 (카드에 연결된 게시물)   # 해당 도서와 연결된 GeneralPost 객체 생성 (카드에 연결된 게시물)
            title='카드 테스트 게시물',                                             # 게시물 제목                          # 게시물 제목                          
            content='카드 테스트 게시물 내용',                                    # 게시물 내용                          # 게시물 내용                          
            writer=dummy_user,                                                    # 작성자 (NOT NULL 문제 해결)          # 작성자 (NOT NULL 문제 해결)           
            category='일반',                                                  # 카테고리 (올바른 선택값 사용)         # 카테고리 (올바른 선택값 사용)           
            book=self.book                                                        # 연관 도서 지정                      # 연관 도서 지정                      
        )

    def test_get_posts_by_book(self):
        url = reverse('community:get_posts_by_book')                              # 요청 URL 역참조                    # 요청 URL 역참조                    
        response = self.client.get(url, {'isbn': self.book.isbn})                   # ISBN으로 GET 요청                    # ISBN으로 GET 요청                    
        self.assertEqual(response.status_code, 200)                                # 상태 코드 200 확인                  # 상태 코드 200 확인                  
        data = json.loads(response.content)                                       # 응답 JSON 디코드                    # 응답 JSON 디코드                    
        self.assertEqual(data.get('status'), 'success')                           # 응답 상태 'success' 확인           # 응답 상태 'success' 확인           
        self.assertEqual(data.get('book_title'), self.book.title)                 # 도서 제목 확인                      # 도서 제목 확인                      
        posts = data.get('posts', [])                                             # 게시물 리스트 추출                  # 게시물 리스트 추출                  
        self.assertTrue(len(posts) > 0)                                             # 게시물이 하나 이상 있는지 확인      # 게시물이 하나 이상 있는지 확인      

    def test_home_page_contains_book_card(self):
        home_url = reverse('community:home')                                       # 홈 URL 역참조                      # 홈 URL 역참조                    
        response = self.client.get(home_url)                                      # 홈 페이지 GET 요청                  # 홈 페이지 GET 요청                  
        self.assertEqual(response.status_code, 200)                               # 응답 상태 코드 200 확인             # 응답 상태 코드 200 확인            
        self.assertContains(response, self.book.title)                            # 홈 페이지에 도서 제목 포함 여부 확인   # 홈 페이지에 도서 제목 포함 여부 확인  

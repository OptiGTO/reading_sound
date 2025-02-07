# community/forms.py

from django import forms
from .models import GeneralPost, BookReviewEventPost, PersonalBookEventPost, ReadingGroupPost, ReadingTipPost, PostTag ,Comment, BookTalkEventPost, BookGenre, Book
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
User = get_user_model()


class PostForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '제목을 입력하세요'
        }), 
        required=True
    )  # 제목 입력 필드

    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': '내용을 입력하세요',
            'rows': 10
        }), 
        required=True
    )  # 내용 입력 필드

    category = forms.ChoiceField(
        choices=(
            ('book_post', '책 게시글'),
            ('reading_group_post', '독서 모임'),
            ('book_review_event', '서평 이벤트'),
            ('book_talk_post', '북토크'),
            ('personal_event_post', '개인 이벤트'),
        ),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )  # 카테고리 선택 필드

    tags = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '태그를 쉼표(,)로 구분하여 입력하세요'
        })
    )  # 태그 입력 필드

    genre = forms.ChoiceField(
        choices=BookGenre.choices,  # 모델의 선택 항목 직접 참조
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="책 장르"  # 레이블 한국어로 명시적 설정
    )  # 카테고리 선택 필드


    class Meta:
        model = GeneralPost
        fields = ['title', 'content', 'category', 'tags', 'genre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 부모 초기화 호출
        # POST 데이터나 초기값에서 category를 가져오고, 없으면 기본값 'book_post'로 설정
        category = self.data.get('category') or self.initial.get('category') or 'book_post'

        # 동적 필드를 항상 추가하고, 기본 required는 False로 설정하여 화면에 렌더링하되 CSS로 숨깁니다.
        self.fields['event_date'] = forms.DateField(
            required=False,                                                                          # 카테고리에 따라 검증할 예정
            widget=forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': '이벤트 날짜 (YYYY-MM-DD)',
                'style': 'display:none;'                                                            # 초기 숨김 처리
            })
        )  # 독서 모임용 이벤트 날짜

        self.fields['event_start_date'] = forms.DateTimeField(
            required=False,                                                                          # 동적 검증 후 필수 처리 가능
            widget=forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': '이벤트 시작일시 (YYYY-MM-DD HH:MM)',
                'style': 'display:none;'                                                            # 초기 숨김 처리
            })
        )  # 이벤트 시작일시

        self.fields['event_end_date'] = forms.DateTimeField(
            required=False,                                                                          # 동적 검증 후 필수 처리 가능
            widget=forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': '이벤트 종료일시 (YYYY-MM-DD HH:MM)',
                'style': 'display:none;'                                                            # 초기 숨김 처리
            })
        )  # 이벤트 종료일시

    def clean(self):
        cleaned_data = super().clean()  # 부모의 clean 메소드 호출
        category = cleaned_data.get('category')  # 선택한 카테고리 가져오기
        
        # 카테고리별로 동적 필드의 값 검증
        if category == 'reading_group_post':  # 독서 모임 카테고리인 경우
            if not cleaned_data.get('event_date'):  # 필수 값 검증
                self.add_error('event_date', '독서 모임 게시글의 경우 이벤트 날짜는 필수입니다.')  # 에러 메시지 추가
        elif category in ['book_review_event', 'personal_event_post', 'book_talk_post']:  # 이벤트 관련 카테고리인 경우
            if not cleaned_data.get('event_start_date'):  # 필수 값 검증
                self.add_error('event_start_date', '이벤트 시작일시는 필수입니다.')  # 에러 메시지 추가
            if not cleaned_data.get('event_end_date'):  # 필수 값 검증
                self.add_error('event_end_date', '이벤트 종료일시는 필수입니다.')  # 에러 메시지 추가
        return cleaned_data  # 정제된 데이터 반환
    
    def save(self, commit=True, writer=None):
        CATEGORY_MODEL_MAP = {
            'book_post': GeneralPost,
            'reading_group_post': ReadingGroupPost,
            'book_review_event': BookReviewEventPost,
            'personal_event_post': PersonalBookEventPost,
            'book_talk_post': BookTalkEventPost,
        }  # 카테고리별 모델 매핑

        category = self.cleaned_data.get('category')  # 선택한 카테고리 가져오기
        ModelClass = CATEGORY_MODEL_MAP.get(category, GeneralPost)  # 해당 모델 결정, 기본은 GeneralPost

        instance = ModelClass(
            title=self.cleaned_data.get('title'),
            content=self.cleaned_data.get('content'),
            category=category,  # 카테고리 저장
        )  # 모델 인스턴스 생성
        if writer:
            instance.writer = writer  # 작성자 할당

        # 추가 필드 처리: 카테고리별 이벤트 관련 필드 저장
        if category == 'reading_group_post':
            instance.event_date = self.cleaned_data.get('event_date')  # 독서 모임 이벤트 날짜 저장
        elif category in ['book_review_event', 'personal_event_post', 'book_talk_post']:
            instance.event_start_date = self.cleaned_data.get('event_start_date')  # 이벤트 시작일시 저장
            instance.event_end_date = self.cleaned_data.get('event_end_date')  # 이벤트 종료일시 저장

        if commit:
            instance.save()  # 인스턴스 저장
            # 태그 처리: 콤마(,)로 구분된 태그 문자열을 태그 객체로 변환
            tag_string = self.cleaned_data.get('tags', '')
            tag_names = [name.strip() for name in tag_string.split(',') if name.strip()]  # 태그 이름 리스트 생성
            instance.tags.clear()  # 기존 태그 모두 제거
            from .models import PostTag  # PostTag 모델 임포트
            for tag_name in tag_names:
                tag, _ = PostTag.objects.get_or_create(name=tag_name)  # 태그 객체 생성 또는 가져오기
                instance.tags.add(tag)  # 태그 연결

           

        return instance  # 저장된 인스턴스 반환


#---------------------------------------- 로그인 관련---------------------------------------------------------

class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(
        label="아이디",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="이메일",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": "아이디",
            "password1": "비밀번호",
            "password2": "비밀번호 확인"
        }



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

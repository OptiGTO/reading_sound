# community/forms.py

from django import forms
from .models import GeneralPost, BookEventPost, BookReviewEventPost, ReadingGroupPost, ReadingTipPost, PostTag
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
User = get_user_model()

class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '태그를 쉼표(,)로 구분하여 입력하세요'
        })
    )

    class Meta:
        model = GeneralPost
        fields = ['title', 'content', 'category']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'style': 'width: 100%', 
                'placeholder': '제목을 입력하세요'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control', 
                'style': 'width: 100%', 
                'placeholder': '내용을 입력하세요',
                'rows': 10,
                'cols': 100,
                'height': '600px',
                'toolbar': 'Basic',
                'toolbar_Basic': [
                    ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
                    ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'],
                    ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
                    ['Link', 'Unlink'],
                    ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar'],
                    ['Source'],
                ],
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('title'):
            raise forms.ValidationError('제목을 입력해주세요.')
        if not cleaned_data.get('content'):
            raise forms.ValidationError('내용을 입력해주세요.')
        return cleaned_data

    def clean_tags(self):
        tag_string = self.cleaned_data.get('tags', '')
        if isinstance(tag_string, str):
            tag_names = [name.strip() for name in tag_string.split(',') if name.strip()]
            tags = []
            for tag_name in tag_names:
                tag, _ = PostTag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            return tags
        return tag_string

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # 태그 처리
            tag_names = self.cleaned_data.get('tags', '').split(',')
            tag_names = [name.strip() for name in tag_names if name.strip()]
            instance.tags.clear()
            for tag_name in tag_names:
                tag, _ = PostTag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        return instance


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
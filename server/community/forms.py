# community/forms.py

from django import forms
from .models import Post
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'writer', 'category','image', 'book']
        
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%', 'placeholder': '제목을 입력하세요'}),
                'content': CKEditorUploadingWidget(),
        }
        # 필요하다면 widgets나 labels 등을 커스터마이징할 수 있음.



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
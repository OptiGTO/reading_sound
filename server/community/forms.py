# community/forms.py

from django import forms
from .models import Post
from ckeditor_uploader.widgets import CKEditorUploadingWidget
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'writer', 'category','image', 'book']
        
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%', 'placeholder': '제목을 입력하세요'}),
                'content': CKEditorUploadingWidget(),
        }
        # 필요하다면 widgets나 labels 등을 커스터마이징할 수 있음.

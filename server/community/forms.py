# community/forms.py

from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'writer', 'category', 'book']
        # 필요하다면 widgets나 labels 등을 커스터마이징할 수 있음.

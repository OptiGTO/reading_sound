# community/templatetags/comment_tags.py
from django import template

register = template.Library()

@register.filter
def get_class_name(obj):
    """
    객체의 클래스 이름을 반환합니다.
    예: GeneralPost 객체면 'GeneralPost' 반환
    """
    return obj.__class__.__name__

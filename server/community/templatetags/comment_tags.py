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

@register.filter
def is_liked_by(obj, user):
    """객체가 특정 사용자에 의해 좋아요 되었는지 확인"""
    return obj.is_liked_by(user)

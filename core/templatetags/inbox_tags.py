from django import template
from core.models import Message  # adjust if your model is in another app

register = template.Library()

@register.simple_tag
def get_unread_count(user):
    """Return number of unread messages for a user."""
    if user.is_authenticated:
        return Message.objects.filter(receiver=user, is_read=False).count()
    return 0

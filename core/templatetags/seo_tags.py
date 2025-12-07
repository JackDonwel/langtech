# core/templatetags/seo_tags.py
from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def render_seo(obj=None, page_type=None):
    """Simple SEO tag renderer"""
    context = {}
    
    if obj and hasattr(obj, 'get_seo_context'):
        context = obj.get_seo_context()
    elif page_type:
        if page_type == '/':
            context = {
                'title': 'LangTouch - Language Excellence',
                'description': 'Professional language translation services',
                'keywords': 'translation, language, swahili, english, french',
            }
    
    return render_to_string('core/meta_tags.html', context)
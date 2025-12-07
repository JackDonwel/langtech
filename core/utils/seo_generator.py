# core/utils/seo_generator.py
from django.contrib.contenttypes.models import ContentType
from core.models import SEO

class SEOGenerator:
    @staticmethod
    def create_for_object(obj, page_type=None, **kwargs):
        """Create SEO for any model object"""
        content_type = ContentType.objects.get_for_model(obj)
        
        # Default values
        defaults = {
            'page_type': page_type or obj._meta.model_name,
            'meta_title': getattr(obj, 'seo_title', str(obj)),
            'meta_description': getattr(obj, 'seo_description', ''),
            'meta_keywords': getattr(obj, 'seo_keywords', ''),
            'canonical_url': getattr(obj, 'get_absolute_url', lambda: '')(),
            'is_active': True,
        }
        
        # Update with kwargs
        defaults.update(kwargs)
        
        # Create or update SEO
        seo, created = SEO.objects.update_or_create(
            content_type=content_type,
            object_id=obj.id,
            defaults=defaults
        )
        
        return seo
    
    @staticmethod
    def get_for_object(obj):
        """Get SEO for an object"""
        content_type = ContentType.objects.get_for_model(obj)
        try:
            return SEO.objects.get(content_type=content_type, object_id=obj.id, is_active=True)
        except SEO.DoesNotExist:
            return None
    
    @staticmethod
    def get_for_page(page_type):
        """Get SEO for a page type"""
        try:
            return SEO.objects.get(page_type=page_type, is_active=True)
        except SEO.DoesNotExist:
            return None
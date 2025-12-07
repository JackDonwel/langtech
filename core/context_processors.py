# context_processors.py
from .models import SEO
from django.contrib.contenttypes.models import ContentType

def seo_context(request):
    """Add global SEO data to all templates"""
    context = {
        'seo': None,
        'global_seo': {
            'site_name': 'Langtouch Language Services',
            'default_image': request.build_absolute_uri('/static/images/og-default.jpg'),
            'theme_color': '#3b82f6',
        }
    }
    
    # Try to get page-specific SEO
    try:
        # You would determine content type and object_id based on your view
        # This is a simplified example
        path = request.path_info
        
        if path.startswith('/services/'):
            # Get service-specific SEO
            from .models import Service
            service_slug = path.split('/')[-2]
            service = Service.objects.get(slug=service_slug)
            content_type = ContentType.objects.get_for_model(service)
            seo_obj = SEO.objects.filter(
                content_type=content_type,
                object_id=service.id
            ).first()
            
            if seo_obj:
                context['seo'] = seo_obj
    except:
        pass
    
    return context
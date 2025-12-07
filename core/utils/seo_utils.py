# utils/seo_utils.py
from django.urls import reverse
from core.models import SEO

class SEOGenerator:
    @staticmethod
    def generate_for_service(service):
        """Generate SEO data for a service page"""
        base_url = 'https://langtouch.com'
        
        return {
            'meta_title': f"{service.title} | Langtouch Language Services",
            'meta_description': f"Professional {service.title.lower()} service. {service.excerpt}",
            'meta_keywords': f"{service.title}, language service, Tanzania, Dar es Salaam",
            'canonical_url': f"{base_url}{reverse('service_detail', args=[service.slug])}",
            'og_title': f"Learn {service.title} with Langtouch",
            'og_description': f"Master {service.title} with our certified instructors",
            'og_image_url': service.featured_image.url if service.featured_image else f"{base_url}/static/images/default-og.jpg",
            'breadcrumb_name': service.title,
        }
    
    @staticmethod
    def generate_breadcrumbs(page_title, path_list):
        """Generate breadcrumb schema data"""
        breadcrumbs = []
        for i, (name, url) in enumerate(path_list, 1):
            breadcrumbs.append({
                "position": i,
                "name": name,
                "item": url
            })
        return breadcrumbs
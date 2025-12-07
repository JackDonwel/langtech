# core/management/commands/check_env.py
from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Check environment variables and settings'
    
    def handle(self, *args, **options):
        self.stdout.write('=== Environment Variables Check ===')
        
        # Check environment variable directly
        env_api_key = os.environ.get("GEMINI_API_KEY")
        self.stdout.write(f"os.environ.get('GEMINI_API_KEY'): {bool(env_api_key)}")
        if env_api_key:
            self.stdout.write(f"  First 10 chars: {env_api_key[:10]}...")
        
        # Check Django settings
        self.stdout.write(f"\nsettings.GEMINI_API_KEY: {settings.GEMINI_API_KEY}")
        if settings.GEMINI_API_KEY:
            self.stdout.write(f"  First 10 chars: {settings.GEMINI_API_KEY[:10]}...")
        
        self.stdout.write(f"\nsettings.DEBUG: {settings.DEBUG}")
        self.stdout.write(f"settings.SECRET_KEY set: {bool(settings.SECRET_KEY)}")
        
        # Try to create GeminiService
        try:
            from core.views import GeminiService
            service = GeminiService()
            self.stdout.write(self.style.SUCCESS('\n✅ GeminiService created successfully!'))
            
            # Test a query
            response = service.get_ai_response("Say 'Hello from Django' in 5 words or less.")
            self.stdout.write(self.style.SUCCESS(f'✅ AI Response: {response}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error creating GeminiService: {e}'))
            
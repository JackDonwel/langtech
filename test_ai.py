# test_updated.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'langtouch.settings')
import django
django.setup()

from core.views import GeminiService

try:
    service = GeminiService()
    print("✅ GeminiService created!")
    
    response = service.get_ai_response("Say 'LangTouch AI is working!'")
    print(f"✅ Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
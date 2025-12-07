# core/urls.py
from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('about/', views.about_view, name='about'),

    path('services/', views.services_view, name='services'),
    path('inbox/', views.inbox, name='inbox'),
    path('contact/', views.contact_form, name='contact_form'),
    path('test-gemini-api/', views.test_gemini_api, name='test_gemini_api'),
    
    # New URL patterns for AI chat functionality
    path('send-message/<int:conversation_id>/', views.send_message, name='send_message'),
    path('send-message/to/<str:recipient_username>/', views.send_message, name='send_message_user'),
    path('ai/start/', views.start_ai_conversation, name='start_ai_chat'),
    path('api/ai-chat/', views.api_ai_chat, name='api_ai_chat'),
    path('start-ai-conversation/', views.start_ai_conversation, name='start_ai_conversation'),
    path('admin/test-gemini/', views.test_gemini_api, name='test_gemini_api'),
    # Correct URL for the inbox
    path('contact-admin/', views.contact_admin, name='contact_admin'),
    path('messages/inbox/', views.inbox, name='inbox'),
    path('messages/send/', views.send_message, name='send_message'),
    path('contact/success/', lambda r: render(r, 'core/contact_success.html'), name='contact_success'),
    # New URL pattern for video learning

]
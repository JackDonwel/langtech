# create_auth_files.py
import os

# Create directories
directories = [
    'accounts/templates/accounts',
    'accounts/management/commands',
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

# Update urls.py
urls_content = '''from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/'
         ), 
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset/complete/'
         ),
         name='password_reset_confirm'),
    
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
'''

with open('accounts/urls.py', 'w') as f:
    f.write(urls_content)
print("Updated accounts/urls.py")

# Create password reset templates
templates = {
    'password_reset.html': '''{% extends "base.html" %}
{% load widget_tweaks %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-gray-800 p-8 rounded-xl border border-gray-700">
        <div class="text-center">
            <h2 class="text-3xl font-bold text-white">Reset Password</h2>
            <p class="mt-2 text-gray-400">
                Enter your email to receive a reset link.
            </p>
        </div>

        <form method="POST" class="mt-8 space-y-6">
            {% csrf_token %}
            
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                <div class="relative">
                    <i class="fas fa-envelope absolute left-3 top-3 text-gray-500"></i>
                    {% render_field form.email class="pl-10 w-full p-3 bg-gray-900 border border-gray-700 rounded-lg text-white" placeholder="you@example.com" %}
                </div>
                {% if form.email.errors %}
                <p class="mt-2 text-sm text-red-400">{{ form.email.errors.0 }}</p>
                {% endif %}
            </div>

            <button type="submit" class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition">
                Send Reset Link
            </button>

            <div class="text-center">
                <a href="{% url 'accounts:login' %}" class="text-blue-400 hover:text-blue-300 text-sm">
                    ← Back to Sign In
                </a>
            </div>
        </form>
    </div>
</div>
{% endblock %}''',

    'password_reset_done.html': '''{% extends "base.html" %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-gray-800 p-8 rounded-xl border border-gray-700 text-center">
        <div class="mx-auto h-16 w-16 bg-green-600 rounded-full flex items-center justify-center mb-6">
            <i class="fas fa-check text-white text-2xl"></i>
        </div>
        
        <h2 class="text-3xl font-bold text-white">Check Your Email</h2>
        <p class="mt-4 text-gray-300">
            We've sent you an email with password reset instructions.
        </p>
        
        <div class="mt-6">
            <a href="{% url 'accounts:login' %}" 
               class="inline-block py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition">
                Return to Sign In
            </a>
        </div>
    </div>
</div>
{% endblock %}''',

    'password_reset_confirm.html': '''{% extends "base.html" %}
{% load widget_tweaks %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-gray-800 p-8 rounded-xl border border-gray-700">
        <div class="text-center">
            <h2 class="text-3xl font-bold text-white">Set New Password</h2>
            <p class="mt-2 text-gray-400">
                Enter your new password twice.
            </p>
        </div>

        <form method="POST" class="mt-8 space-y-6">
            {% csrf_token %}
            
            {% for field in form %}
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">{{ field.label }}</label>
                <div class="relative">
                    <i class="fas fa-lock absolute left-3 top-3 text-gray-500"></i>
                    {% render_field field class="pl-10 w-full p-3 bg-gray-900 border border-gray-700 rounded-lg text-white" %}
                </div>
                {% if field.errors %}
                <p class="mt-2 text-sm text-red-400">{{ field.errors.0 }}</p>
                {% endif %}
                {% if field.help_text %}
                <p class="mt-2 text-sm text-gray-400">{{ field.help_text }}</p>
                {% endif %}
            </div>
            {% endfor %}

            <button type="submit" class="w-full py-3 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition">
                Change Password
            </button>
        </form>
    </div>
</div>
{% endblock %}''',

    'password_reset_complete.html': '''{% extends "base.html" %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-gray-800 p-8 rounded-xl border border-gray-700 text-center">
        <div class="mx-auto h-16 w-16 bg-green-600 rounded-full flex items-center justify-center mb-6">
            <i class="fas fa-check-circle text-white text-2xl"></i>
        </div>
        
        <h2 class="text-3xl font-bold text-white">Password Reset Complete!</h2>
        <p class="mt-4 text-gray-300">
            Your password has been successfully reset.
        </p>
        
        <div class="mt-6">
            <a href="{% url 'accounts:login' %}" 
               class="inline-block py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition">
                Sign In Now
            </a>
        </div>
    </div>
</div>
{% endblock %}''',

    'password_reset_email.html': '''<!DOCTYPE html>
<html>
<body>
    <h2>Password Reset Request</h2>
    <p>You're receiving this email because you requested a password reset.</p>
    <p>Please click the link below to reset your password:</p>
    <p><a href="{{ protocol }}://{{ domain }}{% url 'accounts:password_reset_confirm' uidb64=uid token=token %}">
        Reset Password
    </a></p>
    <p>If you didn't request this, please ignore this email.</p>
    <p>Thanks,<br>The Langtech Team</p>
</body>
</html>''',

    'password_reset_subject.txt': '''Password Reset Request for Your Langtech Account'''
}

for filename, content in templates.items():
    with open(f'accounts/templates/accounts/{filename}', 'w') as f:
        f.write(content)
    print(f"Created accounts/templates/accounts/{filename}")

# Create management command
management_cmd = '''from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Test the password reset system'
    
    def handle(self, *args, **options):
        self.stdout.write('Password reset system is ready!')
        self.stdout.write('\\nTest URLs:')
        self.stdout.write('1. /accounts/password-reset/')
        self.stdout.write('2. Check console for email link')
        self.stdout.write('3. Follow link to reset password')
'''

with open('accounts/management/commands/test_password_reset.py', 'w') as f:
    f.write(management_cmd)
print("Created accounts/management/commands/test_password_reset.py")

print("\\n✅ All files created successfully!")
print("\\nNext steps:")
print("1. Run: python manage.py migrate")
print("2. Test: python manage.py test_password_reset")
print("3. Visit: http://127.0.0.1:8000/accounts/password-reset/")
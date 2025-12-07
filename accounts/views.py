# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout # Make sure you import login/logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy # For more robust URL handling
from django.utils import timezone

# Import your custom forms
from .forms import CustomUserCreationForm, CustomAuthenticationForm 
from .models import User, Role, UserRole # Ensure your User, Role, UserRole models are imported

def register_view(request):
    login_form = CustomAuthenticationForm(request) # Instantiate login form for the template
    
    if request.method == 'POST':
        register_form = CustomUserCreationForm(request.POST)
        if register_form.is_valid():
            user = register_form.save() # Saves the user object
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('accounts:login') # Redirect to your login URL name
        else:
            # If form is invalid, re-render with errors
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'accounts/auth.html', {'register_form': register_form, 'form': login_form})
    else:
        register_form = CustomUserCreationForm() # An empty form for GET request
    
    return render(request, 'accounts/auth.html', {'register_form': register_form, 'form': login_form})


def login_view(request):
    register_form = CustomUserCreationForm() # Instantiate register form for the template

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate the user
            user = form.get_user() 
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(reverse_lazy('core:index')) # Use reverse_lazy for redirects outside request-response cycle

        else:
            # If form is invalid, re-render with errors
            messages.error(request, 'Invalid email or password.')
            return render(request, 'accounts/auth.html', {'form': form, 'register_form': register_form})
    else:
        form = CustomAuthenticationForm(request) # An empty form for GET request
    
    return render(request, 'accounts/auth.html', {'form': form, 'register_form': register_form})
@login_required
def password_reset_view(request):
    # This view can be used to initiate password reset for logged-in users
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Your password has been updated successfully.')
            return redirect(reverse_lazy('accounts:login'))
        else:
            messages.error(request, 'Passwords do not match or are invalid.')

    return render(request, 'accounts/password_reset.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect(reverse_lazy('accounts:login')) # Redirect to the login page after logout


@login_required
def assign_role_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')

        try:
            user = User.objects.get(id=int(user_id)) # Ensure user_id is an integer
            role = Role.objects.get(id=int(role_id)) # Ensure role_id is an integer

            # Using update_or_create to ensure 'updated_at' is always current
            # Assuming 'UserRole' model has auto_now=True for 'updated_at'
            user_role, created = UserRole.objects.update_or_create(
                user=user, 
                role=role, 
                defaults={
                    # 'created_at': timezone.now(), # Only set on creation, better to use auto_now_add in model
                    'updated_at': timezone.now() # This will be updated on create or update
                }
            )

            if created:
                messages.success(request, f'Role "{role.name}" assigned to {user.username}')
            else:
                messages.info(request, f'Role "{role.name}" was already assigned to {user.username} (updated timestamp).')

        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Role.DoesNotExist:
            messages.error(request, 'Role not found.')
        except ValueError:
            messages.error(request, 'Invalid user or role ID provided.')

        return redirect(reverse_lazy('assign-role'))

    users = User.objects.all()
    roles = Role.objects.all()
    return render(request, 'accounts/assign_role.html', {'users': users, 'roles': roles})


def services_view(request):
    # This view seems unrelated to accounts, but kept as requested
    return render(request, 'services/services.html')
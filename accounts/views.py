from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def home_view(request):
    """Landing page - redirect based on authentication"""
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('dashboards:admin_dashboard')
        else:
            return redirect('dashboards:user_dashboard')
    return render(request, 'home.html')


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # ✅ SAFE: prevents duplicate profile error
            UserProfile.objects.get_or_create(user=user)

            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                if user.is_admin:
                    return redirect('dashboards:admin_dashboard')
                else:
                    return redirect('dashboards:user_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view + update"""

    # ✅ Always safe (no crash even if profile missing)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form})
"""
Enhanced views for the MikroTik Hotspot Platform with role-based access
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import User, UserProfile, Provider, EndUser, SuperAdmin, Cashier
from .serializers import UserSerializer, UserProfileSerializer, UserLoginSerializer
from .decorators import (
    super_admin_required, provider_required, cashier_required,
    provider_or_cashier_required, revenue_access_required,
    router_config_access_required, user_management_access_required
)

# HTML Form Views
class RegistrationFormView(TemplateView):
    template_name = 'accounts/register.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type', 'provider')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, self.template_name)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, self.template_name)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, self.template_name)
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Create role-specific profiles
            if user_type == 'provider':
                Provider.objects.create(
                    user=user,
                    business_name=f"{first_name} {last_name} Business",
                    license_number=f"LIC-{user.id}",
                    contact_person=f"{first_name} {last_name}",
                    contact_phone="",
                    contact_email=email,
                    address="",
                    city="",
                    county="",
                    country="Kenya"
                )
            # Note: Cashier accounts are now created by providers through the super admin dashboard
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, self.template_name)


class LoginFormView(TemplateView):
    template_name = 'accounts/login.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Redirect based on user type
            if user.is_superuser or user.is_super_admin:
                return redirect('super_admin:dashboard')
            elif user.is_provider():
                return redirect('provider:dashboard')
            elif user.is_cashier():
                return redirect('cashier:dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
            return render(request, self.template_name)


def logout_form_view(request):
    """Logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """API logout view"""
    try:
        request.user.auth_token.delete()
    except:
        pass
    return Response({'message': 'Logged out successfully'})


@login_required
def dashboard(request):
    """Main dashboard - redirects based on user type"""
    if request.user.is_superuser or request.user.is_super_admin:
        return redirect('super_admin:dashboard')
    elif request.user.is_provider():
        return redirect('provider:dashboard')
    elif request.user.is_cashier():
        return redirect('cashier:dashboard')
    else:
        return render(request, 'accounts/end_user_dashboard.html', {
            'user': request.user,
            'page_title': 'Your Dashboard'
        })


@super_admin_required
def super_admin_dashboard(request):
    """Super Admin Dashboard"""
    # Global statistics
    total_providers = Provider.objects.count()
    active_providers = Provider.objects.filter(status='active').count()
    total_cashiers = Cashier.objects.count()
    total_end_users = EndUser.objects.count()
    
    # Recent activity
    recent_providers = Provider.objects.order_by('-created_at')[:5]
    recent_cashiers = Cashier.objects.order_by('-created_at')[:5]
    
    context = {
        'total_providers': total_providers,
        'active_providers': active_providers,
        'total_cashiers': total_cashiers,
        'total_end_users': total_end_users,
        'recent_providers': recent_providers,
        'recent_cashiers': recent_cashiers,
        'page_title': 'Super Admin Dashboard'
    }
    return render(request, 'accounts/super_admin_dashboard.html', context)


@provider_required
def provider_dashboard(request):
    """Provider Dashboard"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, "Provider profile not found.")
        return redirect('home')
    
    # Provider statistics
    total_cashiers = Cashier.objects.filter(provider=provider).count()
    active_cashiers = Cashier.objects.filter(provider=provider, status='active').count()
    total_end_users = EndUser.objects.filter(provider=provider).count()
    
    # Recent cashiers
    recent_cashiers = Cashier.objects.filter(provider=provider).order_by('-created_at')[:5]
    
    context = {
        'provider': provider,
        'total_cashiers': total_cashiers,
        'active_cashiers': active_cashiers,
        'total_end_users': total_end_users,
        'recent_cashiers': recent_cashiers,
        'page_title': f'{provider.business_name} Dashboard'
    }
    return render(request, 'accounts/provider_dashboard.html', context)


@cashier_required
def cashier_dashboard(request):
    """Cashier Dashboard"""
    try:
        cashier = request.user.cashier_profile
        provider = cashier.provider
    except Cashier.DoesNotExist:
        messages.error(request, "Cashier profile not found.")
        return redirect('home')
    
    # Cashier statistics (limited based on permissions)
    context = {
        'cashier': cashier,
        'provider': provider,
        'can_view_sales': cashier.can_view_sales,
        'can_generate_tickets': cashier.can_generate_tickets,
        'can_sell_tickets': cashier.can_sell_tickets,
        'page_title': f'Cashier Dashboard - {provider.business_name}'
    }
    return render(request, 'accounts/cashier_dashboard.html', context)


# API Views
class UserRegistrationView(generics.CreateAPIView):
    """API view for user registration"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Create role-specific profiles
            if user.user_type == 'provider':
                Provider.objects.create(
                    user=user,
                    business_name=f"{user.first_name} {user.last_name} Business",
                    license_number=f"LIC-{user.id}",
                    contact_person=f"{user.first_name} {user.last_name}",
                    contact_phone="",
                    contact_email=user.email,
                    address="",
                    city="",
                    county="",
                    country="Kenya"
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """API view for user login"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    """Get current user information"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile API view"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile
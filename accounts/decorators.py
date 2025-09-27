"""
Access control decorators for the MikroTik Hotspot Platform
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def super_admin_required(view_func):
    """Require Super Admin access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_super_admin_user():
            messages.error(request, 'Access denied. Super Admin privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def provider_required(view_func):
    """Require Provider access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_provider():
            messages.error(request, 'Access denied. Provider privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def cashier_required(view_func):
    """Require Cashier/Operator access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_cashier():
            messages.error(request, 'Access denied. Cashier privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def provider_or_cashier_required(view_func):
    """Require Provider or Cashier access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_provider_or_cashier():
            messages.error(request, 'Access denied. Provider or Cashier privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def revenue_access_required(view_func):
    """Require revenue management access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.can_manage_revenue():
            messages.error(request, 'Access denied. Revenue management privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def router_config_access_required(view_func):
    """Require router configuration access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.can_manage_router_configs():
            messages.error(request, 'Access denied. Router configuration privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def user_management_access_required(view_func):
    """Require user management access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.can_manage_users():
            messages.error(request, 'Access denied. User management privileges required.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def cashier_permission_required(permission):
    """Require specific cashier permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.is_cashier():
                messages.error(request, 'Access denied. Cashier privileges required.')
                return redirect('dashboard')
            
            # Check if cashier has the specific permission
            try:
                cashier = request.user.cashier_profile
                if not getattr(cashier, permission, False):
                    messages.error(request, f'Access denied. {permission.replace("_", " ").title()} permission required.')
                    return redirect('dashboard')
            except:
                messages.error(request, 'Access denied. Cashier profile not found.')
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

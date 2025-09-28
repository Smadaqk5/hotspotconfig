from django.urls import path
from . import dashboard

app_name = 'super_admin'

urlpatterns = [
    # Dashboard
    path('', dashboard.super_admin_dashboard, name='dashboard'),
    
    # Provider Management
    path('providers/', dashboard.provider_management, name='provider_management'),
    path('providers/<int:provider_id>/', dashboard.provider_detail, name='provider_detail'),
    path('providers/<int:provider_id>/update-status/', dashboard.update_provider_status, name='update_provider_status'),
    
    # Analytics
    path('analytics/', dashboard.global_analytics, name='analytics'),
    
    # System Settings
    path('settings/', dashboard.system_settings, name='system_settings'),
]
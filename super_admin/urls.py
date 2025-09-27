from django.urls import path
from . import views

app_name = 'super_admin'

urlpatterns = [
    # Dashboard
    path('', views.super_admin_dashboard, name='dashboard'),
    
    # Provider Management
    path('providers/', views.providers_list, name='providers'),
    path('providers/<int:provider_id>/', views.provider_detail, name='provider_detail'),
    path('providers/<int:provider_id>/approve/', views.approve_provider, name='approve_provider'),
    path('providers/<int:provider_id>/suspend/', views.suspend_provider, name='suspend_provider'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # API Endpoints
    path('api/stats/', views.api_global_stats, name='api_global_stats'),
    path('api/providers/<int:provider_id>/stats/', views.api_provider_stats, name='api_provider_stats'),
]

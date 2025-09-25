"""
API URL patterns for MikroTik Hotspot Config Generator
"""
from django.urls import path, include
from . import views

# API URL patterns
api_patterns = [
    # Health and stats
    path('health/', views.api_health_check, name='api_health'),
    path('stats/', views.APIStatsView.as_view(), name='api_stats'),
    path('user-stats/', views.UserStatsView.as_view(), name='user_stats'),
    
    # Public endpoints (no authentication required)
    path('public/plans/', views.PublicPlansView.as_view(), name='public_plans'),
    path('public/models/', views.PublicModelsView.as_view(), name='public_models'),
    path('public/voucher-types/', views.PublicVoucherTypesView.as_view(), name='public_voucher_types'),
    path('public/bandwidth-profiles/', views.PublicBandwidthProfilesView.as_view(), name='public_bandwidth_profiles'),
    path('public/templates/', views.PublicTemplatesView.as_view(), name='public_templates'),
    
    # User dashboard
    path('dashboard/', views.user_dashboard_data, name='user_dashboard'),
    
    # Config generation
    path('generate-config/', views.generate_config_api, name='generate_config_api'),
    
    # Include existing app APIs
    path('auth/', include('accounts.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('payments/', include('payments.urls')),
    path('config/', include('config_generator.urls')),
    path('dashboard/', include('dashboard.urls')),
]

urlpatterns = [
    path('v1/', include(api_patterns)),
]

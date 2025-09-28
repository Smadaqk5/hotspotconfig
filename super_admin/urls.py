from django.urls import path
from . import views

app_name = 'super_admin'

urlpatterns = [
    # Dashboard
    path('', views.super_admin_dashboard, name='dashboard'),
    
    # Provider Management
    path('providers/', views.manage_providers, name='manage_providers'),
    path('providers/approve/', views.approve_providers, name='approve_providers'),
    path('providers/<int:provider_id>/', views.provider_detail, name='provider_detail'),
    path('providers/<int:provider_id>/approve/', views.approve_provider, name='approve_provider'),
    path('providers/<int:provider_id>/suspend/', views.suspend_provider, name='suspend_provider'),
    path('providers/<int:provider_id>/delete/', views.delete_provider, name='delete_provider'),
    path('providers/create/', views.create_provider, name='create_provider'),
    
    # Analytics
    path('analytics/', views.global_analytics, name='global_analytics'),
    path('analytics/revenue/', views.revenue_reports, name='revenue_reports'),
    path('analytics/users/', views.user_analytics, name='user_analytics'),
    path('analytics/providers/', views.provider_analytics, name='provider_analytics'),
    
    # System Management
    path('settings/', views.system_settings, name='system_settings'),
    path('payments/', views.payment_monitoring, name='payment_monitoring'),
    path('logs/', views.platform_logs, name='platform_logs'),
    path('health/', views.system_health, name='system_health'),
    
    # Bulk Actions
    path('bulk/approve/', views.bulk_approve, name='bulk_approve'),
    path('export/', views.export_data, name='export_data'),
]
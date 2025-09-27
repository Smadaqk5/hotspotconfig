from django.urls import path
from . import views
from . import payment_settings

app_name = 'provider'

urlpatterns = [
    # Dashboard
    path('', views.provider_dashboard, name='dashboard'),
    
    # Ticket Management
    path('tickets/', views.ticket_management, name='ticket_management'),
    path('tickets/generate/', views.generate_tickets, name='generate_tickets'),
    path('tickets/view/', views.view_tickets, name='view_tickets'),
    
    # Analytics
    path('analytics/', views.sales_analytics, name='analytics'),
    
    # End Users
    path('end-users/', views.end_users_management, name='end_users_management'),
    
    # Subscription
    path('subscription/', views.subscription_management, name='subscription_management'),
    
    # Payment Settings
    path('payment-settings/', payment_settings.payment_settings, name='payment_settings'),
    path('payment-settings/save/', payment_settings.save_mpesa_credentials, name='save_mpesa_credentials'),
    path('payment-settings/test/', payment_settings.test_mpesa_credentials, name='test_mpesa_credentials'),
    path('payment-settings/clear/', payment_settings.clear_mpesa_credentials, name='clear_mpesa_credentials'),
    path('payment-settings/callback-url/', payment_settings.get_callback_url, name='get_callback_url'),
    
    # Config Download
    path('download-config/', views.download_config, name='download_config'),
    
    # API Endpoints
    path('api/stats/', views.api_provider_stats, name='api_provider_stats'),
]

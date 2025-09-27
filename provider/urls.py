from django.urls import path
from . import views

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
    
    # Config Download
    path('download-config/', views.download_config, name='download_config'),
    
    # API Endpoints
    path('api/stats/', views.api_provider_stats, name='api_provider_stats'),
]

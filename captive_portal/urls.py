"""
URL configuration for captive portal
"""
from django.urls import path
from . import views

app_name = 'captive_portal'

urlpatterns = [
    path('', views.portal_login, name='login'),
    path('provider/<int:provider_id>/', views.portal_login, name='provider_login'),
    path('validate/', views.validate_ticket, name='validate_ticket'),
    path('success/<str:ticket_code>/', views.portal_success, name='success'),
    path('error/', views.portal_error, name='error'),
]

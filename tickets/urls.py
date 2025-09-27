"""
URL configuration for tickets app
"""
from django.urls import path
from .views import tickets_list, tickets_generate

urlpatterns = [
    # HTML views
    path('', tickets_list, name='tickets-list'),
    path('generate/', tickets_generate, name='tickets-generate'),
]

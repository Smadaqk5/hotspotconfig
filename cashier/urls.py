"""
URL configuration for cashier app
"""
from django.urls import path
from . import views

app_name = 'cashier'

urlpatterns = [
    path('', views.cashier_dashboard, name='dashboard'),
    path('generate-tickets/', views.generate_tickets, name='generate_tickets'),
    path('sell-tickets/', views.sell_tickets, name='sell_tickets'),
    path('view-sales/', views.view_sales, name='view_sales'),
    path('view-tickets/', views.view_tickets, name='view_tickets'),
]

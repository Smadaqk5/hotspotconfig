from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('stats/', views.dashboard_stats, name='dashboard_stats'),
    path('subscription/', views.subscription_status, name='subscription_status'),
]

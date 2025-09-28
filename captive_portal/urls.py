from django.urls import path
from . import views

app_name = 'captive_portal'

urlpatterns = [
    # Main captive portal
    path('', views.captive_portal, name='index'),
    
    # Payment processing
    path('payment/', views.initiate_payment, name='initiate_payment'),
    path('payment/status/', views.check_payment_status, name='check_payment_status'),
    
    # Ticket management
    path('ticket/<str:ticket_code>/activate/', views.ticket_activation, name='ticket_activation'),
    path('ticket/<str:ticket_code>/status/', views.ticket_status, name='ticket_status'),
    path('success/<str:ticket_code>/', views.success_page, name='success'),
]
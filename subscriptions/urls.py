from django.urls import path
from . import subscription_views

app_name = 'subscriptions'

urlpatterns = [
    # Subscription Plans
    path('plans/', subscription_views.subscription_plans, name='plans'),
    path('subscribe/<int:plan_id>/', subscription_views.subscribe_to_plan, name='subscribe'),
    
    # My Subscription
    path('my-subscription/', subscription_views.my_subscription, name='my_subscription'),
    path('usage/', subscription_views.subscription_usage, name='usage'),
    
    # Payment Callbacks
    path('callback/', subscription_views.subscription_payment_callback, name='payment_callback'),
    path('status/<int:subscription_id>/', subscription_views.check_subscription_status, name='check_status'),
    
    # Subscription Management
    path('cancel/<int:subscription_id>/', subscription_views.cancel_subscription, name='cancel'),
]
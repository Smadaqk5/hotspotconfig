from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.SubscriptionPlanListView.as_view(), name='plans'),
    path('current/', views.UserSubscriptionView.as_view(), name='current_subscription'),
    path('status/', views.subscription_status, name='subscription_status'),
    path('create/', views.create_subscription, name='create_subscription'),
]

from django.urls import path
from . import views

urlpatterns = [
    # HTML Form Views
    path('register/', views.RegistrationFormView.as_view(), name='register'),
    path('login/', views.LoginFormView.as_view(), name='login'),
    path('logout/', views.logout_form_view, name='logout'),
    
    # API Views
    path('api/register/', views.UserRegistrationView.as_view(), name='api_register'),
    path('api/login/', views.login_view, name='api_login'),
    path('api/logout/', views.logout_view, name='api_logout'),
    path('api/profile/', views.UserProfileView.as_view(), name='api_profile'),
    path('api/user/', views.user_info, name='api_user_info'),
]

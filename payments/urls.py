from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.PaymentCreateView.as_view(), name='create_payment'),
    path('list/', views.PaymentListView.as_view(), name='payment_list'),
    path('status/<uuid:payment_id>/', views.payment_status, name='payment_status'),
    path('pesapal/callback/', views.pesapal_callback, name='pesapal_callback'),
    path('pesapal/ipn/', views.pesapal_ipn, name='pesapal_ipn'),
]

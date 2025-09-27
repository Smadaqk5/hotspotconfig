from django.urls import path
from . import views
from . import bucket_views

urlpatterns = [
    path('create/', views.PaymentCreateView.as_view(), name='create_payment'),
    path('list/', views.PaymentListView.as_view(), name='payment_list'),
    path('status/<uuid:payment_id>/', views.payment_status, name='payment_status'),
    path('pesapal/callback/', views.pesapal_callback, name='pesapal_callback'),
    path('pesapal/ipn/', views.pesapal_ipn, name='pesapal_ipn'),
    
    # Payment Bucket API endpoints
    path('bucket/initiate/', bucket_views.initiate_payment, name='bucket_initiate_payment'),
    path('bucket/status/', bucket_views.query_payment_status, name='bucket_query_status'),
    path('bucket/test-credentials/', bucket_views.test_provider_credentials, name='bucket_test_credentials'),
    path('bucket/callback-url/<int:provider_id>/', bucket_views.get_provider_callback_url, name='bucket_callback_url'),
    path('callback/<int:provider_id>/', bucket_views.mpesa_callback, name='mpesa_callback'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('models/', views.MikroTikModelListView.as_view(), name='mikrotik_models'),
    path('voucher-types/', views.VoucherTypeListView.as_view(), name='voucher_types'),
    path('bandwidth-profiles/', views.BandwidthProfileListView.as_view(), name='bandwidth_profiles'),
    path('templates/', views.ConfigTemplateListView.as_view(), name='config_templates'),
    path('generated/', views.GeneratedConfigListView.as_view(), name='generated_configs'),
    path('generate/', views.generate_config, name='generate_config'),
    path('download/<int:config_id>/', views.download_config, name='download_config'),
    path('preview/<int:config_id>/', views.config_preview, name='config_preview'),
]

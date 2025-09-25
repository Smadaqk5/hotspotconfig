"""
URL patterns for Billing Templates
"""
from django.urls import path, include
from . import views

urlpatterns = [
    # Public endpoints
    path('', views.BillingTemplateListView.as_view(), name='billing_template_list'),
    path('popular/', views.PopularBillingTemplatesView.as_view(), name='popular_billing_templates'),
    path('categories/', views.BillingTemplateCategoriesView.as_view(), name='billing_template_categories'),
    path('category/<int:category_id>/', views.BillingTemplateByCategoryView.as_view(), name='billing_templates_by_category'),
    path('search/', views.BillingTemplateSearchView.as_view(), name='billing_template_search'),
    
    # Template details
    path('<int:pk>/', views.BillingTemplateDetailView.as_view(), name='billing_template_detail'),
    path('<int:pk>/with-categories/', views.BillingTemplateWithCategoriesView.as_view(), name='billing_template_with_categories'),
    path('<int:template_id>/config-data/', views.BillingTemplateConfigDataView.as_view(), name='billing_template_config_data'),
    
    # User-specific endpoints
    path('usage/', views.BillingTemplateUsageView.as_view(), name='billing_template_usage'),
    path('track-usage/', views.track_billing_template_usage, name='track_billing_template_usage'),
    
    # Statistics
    path('stats/', views.BillingTemplateStatsView.as_view(), name='billing_template_stats'),
]

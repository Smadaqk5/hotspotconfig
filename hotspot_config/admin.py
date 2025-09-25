"""
Custom admin site configuration
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin import AdminSite
from django.utils.html import format_html


class CustomAdminSite(AdminSite):
    """Custom admin site with enhanced features"""
    
    site_header = "MikroTik Hotspot Config Admin"
    site_title = "Hotspot Config Admin"
    index_title = "Welcome to Hotspot Config Administration"
    
    def index(self, request, extra_context=None):
        """Custom admin index page"""
        extra_context = extra_context or {}
        
        # Get quick stats
        from accounts.models import User
        from subscriptions.models import SubscriptionPlan, Subscription
        from payments.models import Payment
        from config_generator.models import GeneratedConfig
        
        stats = {
            'total_users': User.objects.count(),
            'active_subscriptions': Subscription.objects.filter(is_active=True).count(),
            'total_plans': SubscriptionPlan.objects.count(),
            'total_payments': Payment.objects.count(),
            'generated_configs': GeneratedConfig.objects.count(),
        }
        
        extra_context['stats'] = stats
        
        return super().index(request, extra_context)
    
    def get_urls(self):
        """Add custom URLs"""
        urls = super().get_urls()
        custom_urls = [
            path('subscription-dashboard/', self.admin_view(self.subscription_dashboard), name='subscription_dashboard'),
        ]
        return custom_urls + urls
    
    def subscription_dashboard(self, request):
        """Subscription dashboard view"""
        from subscriptions.admin_dashboard import SubscriptionDashboard
        dashboard = SubscriptionDashboard(self)
        return dashboard.dashboard_view(request)


# Create custom admin site
admin_site = CustomAdminSite(name='hotspot_admin')

# Register models with custom admin site
from django.contrib.auth.models import Group
from accounts.models import User, UserProfile
from subscriptions.models import SubscriptionPlan, Subscription, SubscriptionUsage
from payments.models import Payment, PaymentItem
from config_generator.models import MikroTikModel, VoucherType, BandwidthProfile, ConfigTemplate, GeneratedConfig

# Register all models
admin_site.register(Group)
admin_site.register(User)
admin_site.register(UserProfile)
admin_site.register(SubscriptionPlan)
admin_site.register(Subscription)
admin_site.register(SubscriptionUsage)
admin_site.register(Payment)
admin_site.register(PaymentItem)
admin_site.register(MikroTikModel)
admin_site.register(VoucherType)
admin_site.register(BandwidthProfile)
admin_site.register(ConfigTemplate)
admin_site.register(GeneratedConfig)

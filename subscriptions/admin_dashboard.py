"""
Admin dashboard for subscription management
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, Subscription, SubscriptionUsage


class SubscriptionDashboard:
    """Custom admin dashboard for subscription management"""
    
    def __init__(self, admin_site):
        self.admin_site = admin_site
    
    def dashboard_view(self, request):
        """Main dashboard view"""
        # Get statistics
        stats = self.get_dashboard_stats()
        
        # Get recent activity
        recent_activity = self.get_recent_activity()
        
        # Get plan performance
        plan_performance = self.get_plan_performance()
        
        context = {
            'title': 'Subscription Dashboard',
            'stats': stats,
            'recent_activity': recent_activity,
            'plan_performance': plan_performance,
            'opts': SubscriptionPlan._meta,
            'has_view_permission': True,
        }
        
        return render(request, 'admin/subscriptions/dashboard.html', context)
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        # Total statistics
        total_plans = SubscriptionPlan.objects.count()
        active_plans = SubscriptionPlan.objects.filter(is_active=True).count()
        total_subscriptions = Subscription.objects.count()
        active_subscriptions = Subscription.objects.filter(is_active=True, status='active').count()
        
        # Revenue statistics
        total_revenue = Subscription.objects.aggregate(
            total=Sum('plan__price')
        )['total'] or 0
        
        monthly_revenue = Subscription.objects.filter(
            created_at__gte=last_30_days
        ).aggregate(
            total=Sum('plan__price')
        )['total'] or 0
        
        # Average subscription value
        avg_subscription_value = Subscription.objects.aggregate(
            avg=Avg('plan__price')
        )['avg'] or 0
        
        return {
            'total_plans': total_plans,
            'active_plans': active_plans,
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'avg_subscription_value': avg_subscription_value,
        }
    
    def get_recent_activity(self):
        """Get recent subscription activity"""
        return Subscription.objects.select_related('user', 'plan').order_by('-created_at')[:10]
    
    def get_plan_performance(self):
        """Get plan performance metrics"""
        return SubscriptionPlan.objects.annotate(
            subscriber_count=Count('subscription', filter=Subscription.objects.filter(is_active=True, status='active').query),
            total_revenue=Sum('subscription__plan__price')
        ).order_by('-subscriber_count')
    
    def get_urls(self):
        """Get custom URLs"""
        return [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='subscriptions_dashboard'),
        ]


# Add dashboard to admin site
def add_dashboard_to_admin(admin_site):
    """Add dashboard to admin site"""
    dashboard = SubscriptionDashboard(admin_site)
    original_get_urls = admin_site.get_urls
    admin_site.get_urls = lambda: dashboard.get_urls() + original_get_urls()

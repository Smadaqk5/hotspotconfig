from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from accounts.models import User, Provider, Cashier
from tickets.models import Ticket, TicketSale, TicketType
from payments.models import Payment
from subscriptions.models import ProviderSubscription

def is_super_admin(user):
    """Check if user is a super admin"""
    return user.is_authenticated and (user.is_super_admin or user.user_type == 'super_admin')

@login_required
@user_passes_test(is_super_admin)
def super_admin_dashboard(request):
    """Super Admin Dashboard with global statistics"""
    
    # Global Statistics
    total_providers = Provider.objects.count()
    active_providers = Provider.objects.filter(status='active').count()
    pending_providers = Provider.objects.filter(status='pending').count()
    
    # Revenue Statistics
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Ticket Statistics
    total_tickets_sold = TicketSale.objects.count()
    active_tickets = Ticket.objects.filter(status='active').count()
    expired_tickets = Ticket.objects.filter(status='expired').count()
    
    # Recent Activity
    recent_providers = Provider.objects.order_by('-created_at')[:5]
    recent_payments = Payment.objects.filter(status='completed').order_by('-created_at')[:10]
    
    # Provider Performance (Top 5 by revenue)
    provider_performance = Provider.objects.annotate(
        total_revenue=Sum('payments__amount', filter=Q(payments__status='completed'))
    ).order_by('-total_revenue')[:5]
    
    # Monthly Revenue Chart Data (Last 12 months)
    monthly_revenue = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        month_revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(month_revenue)
        })
    
    monthly_revenue.reverse()
    
    # System Health
    system_health = {
        'database_status': 'healthy',
        'payment_system': 'operational',
        'last_backup': timezone.now() - timedelta(hours=2),
        'active_sessions': 0  # This would be calculated from active tickets
    }
    
    context = {
        'page_title': 'Super Admin Dashboard',
        'total_providers': total_providers,
        'active_providers': active_providers,
        'pending_providers': pending_providers,
        'total_revenue': total_revenue,
        'total_tickets_sold': total_tickets_sold,
        'active_tickets': active_tickets,
        'expired_tickets': expired_tickets,
        'recent_providers': recent_providers,
        'recent_payments': recent_payments,
        'provider_performance': provider_performance,
        'monthly_revenue': json.dumps(monthly_revenue),
        'system_health': system_health,
    }
    
    return render(request, 'super_admin/dashboard.html', context)

@login_required
@user_passes_test(is_super_admin)
def provider_management(request):
    """Manage all providers"""
    
    # Filter providers
    status_filter = request.GET.get('status', 'all')
    search = request.GET.get('search', '')
    
    providers = Provider.objects.all()
    
    if status_filter != 'all':
        providers = providers.filter(status=status_filter)
    
    if search:
        providers = providers.filter(
            Q(business_name__icontains=search) |
            Q(contact_email__icontains=search) |
            Q(license_number__icontains=search)
        )
    
    providers = providers.order_by('-created_at')
    
    context = {
        'page_title': 'Provider Management',
        'providers': providers,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'super_admin/provider_management.html', context)

@login_required
@user_passes_test(is_super_admin)
def provider_detail(request, provider_id):
    """Detailed view of a specific provider"""
    
    provider = get_object_or_404(Provider, id=provider_id)
    
    # Provider Statistics
    provider_stats = {
        'total_tickets': Ticket.objects.filter(provider=provider).count(),
        'active_tickets': Ticket.objects.filter(provider=provider, status='active').count(),
        'total_revenue': Payment.objects.filter(provider=provider, status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'subscription_status': provider.subscription_status,
    }
    
    # Recent Activity
    recent_tickets = Ticket.objects.filter(provider=provider).order_by('-created_at')[:10]
    recent_payments = Payment.objects.filter(provider=provider).order_by('-created_at')[:10]
    
    # Performance Metrics
    performance_metrics = {
        'tickets_this_month': Ticket.objects.filter(
            provider=provider,
            created_at__gte=timezone.now().replace(day=1)
        ).count(),
        'revenue_this_month': Payment.objects.filter(
            provider=provider,
            status='completed',
            created_at__gte=timezone.now().replace(day=1)
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    context = {
        'page_title': f'Provider: {provider.business_name}',
        'provider': provider,
        'provider_stats': provider_stats,
        'recent_tickets': recent_tickets,
        'recent_payments': recent_payments,
        'performance_metrics': performance_metrics,
    }
    
    return render(request, 'super_admin/provider_detail.html', context)

@login_required
@user_passes_test(is_super_admin)
def update_provider_status(request, provider_id):
    """Update provider status (approve, suspend, etc.)"""
    
    provider = get_object_or_404(Provider, id=provider_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        reason = request.POST.get('reason', '')
        
        if new_status in ['active', 'suspended', 'pending', 'rejected']:
            provider.status = new_status
            provider.approved_by = request.user
            provider.approved_at = timezone.now()
            provider.save()
            
            messages.success(request, f'Provider status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('super_admin:provider_detail', provider_id=provider.id)

@login_required
@user_passes_test(is_super_admin)
def global_analytics(request):
    """Global analytics and reporting"""
    
    # Time period filter
    period = request.GET.get('period', '30')  # days
    days = int(period)
    start_date = timezone.now() - timedelta(days=days)
    
    # Revenue Analytics
    revenue_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        daily_revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=date,
            created_at__lt=next_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    
    # Provider Analytics
    provider_analytics = Provider.objects.annotate(
        total_tickets=Count('tickets'),
        total_revenue=Sum('payments__amount', filter=Q(payments__status='completed'))
    ).order_by('-total_revenue')[:10]
    
    # Ticket Type Analytics
    ticket_type_analytics = TicketType.objects.annotate(
        total_sales=Count('ticketsales')
    ).order_by('-total_sales')
    
    context = {
        'page_title': 'Global Analytics',
        'revenue_data': json.dumps(revenue_data),
        'provider_analytics': provider_analytics,
        'ticket_type_analytics': ticket_type_analytics,
        'period': period,
        'days': days,
    }
    
    return render(request, 'super_admin/analytics.html', context)

@login_required
@user_passes_test(is_super_admin)
def system_settings(request):
    """System settings and configuration"""
    
    context = {
        'page_title': 'System Settings',
    }
    
    return render(request, 'super_admin/settings.html', context)

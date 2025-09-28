from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
import csv

from accounts.models import User, Provider
from tickets.models import Ticket, TicketSale, TicketType
from subscriptions.models import ProviderSubscription, ProviderSubscriptionPlan
from payments.models import Payment

def is_super_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_super_admin)
def super_admin_dashboard(request):
    """Super Admin Dashboard"""
    # Platform Statistics
    total_providers = Provider.objects.count()
    active_providers = Provider.objects.filter(status='active').count()
    pending_providers = Provider.objects.filter(status='pending').count()
    
    total_tickets_sold = TicketSale.objects.aggregate(total=Sum('quantity'))['total'] or 0
    total_revenue = TicketSale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_end_users = User.objects.filter(user_type='end_user').count()
    
    # Recent providers
    recent_providers = Provider.objects.order_by('-created_at')[:5]
    
    # Recent sales
    recent_sales = TicketSale.objects.order_by('-created_at')[:5]
    
    context = {
        'page_title': 'Super Admin Dashboard',
        'total_providers': total_providers,
        'active_providers': active_providers,
        'pending_providers': pending_providers,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
        'total_end_users': total_end_users,
        'recent_providers': recent_providers,
        'recent_sales': recent_sales,
    }
    return render(request, 'super_admin/dashboard.html', context)

@login_required
@user_passes_test(is_super_admin)
def manage_providers(request):
    """Manage all providers"""
    providers = Provider.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        providers = providers.filter(status=status_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        providers = providers.filter(
            Q(business_name__icontains=search) |
            Q(contact_email__icontains=search) |
            Q(contact_person__icontains=search)
        )
    
    context = {
        'page_title': 'Manage Providers',
        'providers': providers,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'super_admin/manage_providers.html', context)

@login_required
@user_passes_test(is_super_admin)
def provider_detail(request, provider_id):
    """View and manage a specific provider"""
    provider = get_object_or_404(Provider, id=provider_id)
    
    # Get provider statistics
    provider_tickets = Ticket.objects.filter(provider=provider)
    provider_sales = TicketSale.objects.filter(ticket__provider=provider)
    
    total_tickets = provider_tickets.count()
    total_sales = provider_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_quantity = provider_sales.aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'page_title': f'Provider: {provider.business_name}',
        'provider': provider,
        'total_tickets': total_tickets,
        'total_sales': total_sales,
        'total_quantity': total_quantity,
    }
    return render(request, 'super_admin/provider_detail.html', context)

@login_required
@user_passes_test(is_super_admin)
def approve_provider(request, provider_id):
    """Approve a pending provider"""
    provider = get_object_or_404(Provider, id=provider_id)
    if request.method == 'POST':
        provider.status = 'active'
        provider.is_approved = True
        provider.approved_at = timezone.now()
        provider.approved_by = request.user
        provider.save()
        messages.success(request, f'Provider {provider.business_name} approved.')
    return redirect('super_admin:manage_providers')

@login_required
@user_passes_test(is_super_admin)
def suspend_provider(request, provider_id):
    """Suspend an active provider"""
    provider = get_object_or_404(Provider, id=provider_id)
    if request.method == 'POST':
        provider.status = 'suspended'
        provider.save()
        messages.warning(request, f'Provider {provider.business_name} suspended.')
    return redirect('super_admin:manage_providers')

@login_required
@user_passes_test(is_super_admin)
def delete_provider(request, provider_id):
    """Delete a provider"""
    provider = get_object_or_404(Provider, id=provider_id)
    if request.method == 'POST':
        provider.delete()
        messages.error(request, f'Provider {provider.business_name} deleted.')
    return redirect('super_admin:manage_providers')

@login_required
@user_passes_test(is_super_admin)
def global_analytics(request):
    """Global analytics and reports"""
    # Example: Tickets sold over time
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    sales_data = TicketSale.objects.filter(
        created_at__range=(start_date, end_date)
    ).annotate(
        date=F('created_at__date')
    ).values('date').annotate(
        total_sales=Sum('total_amount'),
        ticket_count=Sum('quantity')
    ).order_by('date')
    
    # Example: Ticket type distribution
    ticket_type_analytics = TicketSale.objects.values(
        'ticket_type__name'
    ).annotate(
        total_sales=Sum('total_amount'),
        ticket_count=Sum('quantity')
    ).order_by('-total_sales')
    
    context = {
        'page_title': 'Global Analytics',
        'sales_data': list(sales_data),
        'ticket_type_analytics': ticket_type_analytics,
        'period': days,
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

# Additional placeholder views
@login_required
@user_passes_test(is_super_admin)
def approve_providers(request):
    """Bulk approve providers"""
    pending_providers = Provider.objects.filter(status='pending')
    context = {
        'page_title': 'Approve Providers',
        'pending_providers': pending_providers,
    }
    return render(request, 'super_admin/approve_providers.html', context)

@login_required
@user_passes_test(is_super_admin)
def create_provider(request):
    """Create new provider"""
    context = {
        'page_title': 'Create Provider',
    }
    return render(request, 'super_admin/create_provider.html', context)

@login_required
@user_passes_test(is_super_admin)
def revenue_reports(request):
    """Revenue reports"""
    total_revenue = TicketSale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    context = {
        'page_title': 'Revenue Reports',
        'total_revenue': total_revenue,
    }
    return render(request, 'super_admin/revenue_reports.html', context)

@login_required
@user_passes_test(is_super_admin)
def user_analytics(request):
    """User analytics"""
    total_users = User.objects.count()
    context = {
        'page_title': 'User Analytics',
        'total_users': total_users,
    }
    return render(request, 'super_admin/user_analytics.html', context)

@login_required
@user_passes_test(is_super_admin)
def provider_analytics(request):
    """Provider analytics"""
    total_providers = Provider.objects.count()
    context = {
        'page_title': 'Provider Analytics',
        'total_providers': total_providers,
    }
    return render(request, 'super_admin/provider_analytics.html', context)

@login_required
@user_passes_test(is_super_admin)
def payment_monitoring(request):
    """Payment monitoring"""
    context = {
        'page_title': 'Payment Monitoring',
    }
    return render(request, 'super_admin/payment_monitoring.html', context)

@login_required
@user_passes_test(is_super_admin)
def platform_logs(request):
    """Platform logs"""
    context = {
        'page_title': 'Platform Logs',
    }
    return render(request, 'super_admin/platform_logs.html', context)

@login_required
@user_passes_test(is_super_admin)
def system_health(request):
    """System health"""
    context = {
        'page_title': 'System Health',
    }
    return render(request, 'super_admin/system_health.html', context)

@login_required
@user_passes_test(is_super_admin)
def bulk_approve(request):
    """Bulk approve providers"""
    context = {
        'page_title': 'Bulk Approve',
    }
    return render(request, 'super_admin/bulk_approve.html', context)

@login_required
@user_passes_test(is_super_admin)
def export_data(request):
    """Export data"""
    context = {
        'page_title': 'Export Data',
    }
    return render(request, 'super_admin/export_data.html', context)
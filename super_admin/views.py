from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User, Provider, EndUser
from tickets.models import Ticket, TicketSale, TicketType
from subscriptions.models import ProviderSubscription, ProviderSubscriptionPlan
from payments.models import Payment
from .models import SystemSettings, PlatformAnalytics, ProviderCommission, SystemNotification


def is_super_admin(user):
    """Check if user is super admin"""
    return user.is_authenticated and (user.is_superuser or user.user_type == 'super_admin')


@login_required
@user_passes_test(is_super_admin)
def super_admin_dashboard(request):
    """Super Admin Dashboard"""
    # Get current date and date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Provider statistics
    total_providers = Provider.objects.count()
    active_providers = Provider.objects.filter(status='active', is_approved=True).count()
    pending_providers = Provider.objects.filter(status='pending').count()
    suspended_providers = Provider.objects.filter(status='suspended').count()
    
    # Recent providers
    recent_providers = Provider.objects.filter(
        created_at__gte=week_ago
    ).order_by('-created_at')[:5]
    
    # Ticket statistics
    total_tickets = Ticket.objects.count()
    active_tickets = Ticket.objects.filter(status='active').count()
    expired_tickets = Ticket.objects.filter(status='expired').count()
    used_tickets = Ticket.objects.filter(status='used').count()
    
    # Revenue statistics
    total_revenue = TicketSale.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    monthly_revenue = TicketSale.objects.filter(
        sold_at__gte=month_ago
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    weekly_revenue = TicketSale.objects.filter(
        sold_at__gte=week_ago
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Top performing providers
    top_providers = Provider.objects.annotate(
        ticket_count=Count('tickets'),
        revenue=Sum('ticket_sales__total_amount')
    ).order_by('-revenue')[:5]
    
    # Recent activity
    recent_ticket_sales = TicketSale.objects.select_related(
        'provider', 'ticket'
    ).order_by('-sold_at')[:10]
    
    # System notifications
    notifications = SystemNotification.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]
    
    context = {
        'page_title': 'Super Admin Dashboard',
        'total_providers': total_providers,
        'active_providers': active_providers,
        'pending_providers': pending_providers,
        'suspended_providers': suspended_providers,
        'recent_providers': recent_providers,
        'total_tickets': total_tickets,
        'active_tickets': active_tickets,
        'expired_tickets': expired_tickets,
        'used_tickets': used_tickets,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'weekly_revenue': weekly_revenue,
        'top_providers': top_providers,
        'recent_ticket_sales': recent_ticket_sales,
        'notifications': notifications,
    }
    
    return render(request, 'super_admin/dashboard.html', context)


@login_required
@user_passes_test(is_super_admin)
def providers_list(request):
    """List all providers"""
    providers = Provider.objects.select_related('user').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        providers = providers.filter(status=status_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        providers = providers.filter(
            Q(business_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(contact_person__icontains=search)
        )
    
    context = {
        'page_title': 'Providers Management',
        'providers': providers,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'super_admin/providers_list.html', context)


@login_required
@user_passes_test(is_super_admin)
def provider_detail(request, provider_id):
    """Provider detail view"""
    provider = get_object_or_404(Provider, id=provider_id)
    
    # Provider statistics
    total_tickets = Ticket.objects.filter(provider=provider).count()
    active_tickets = Ticket.objects.filter(provider=provider, status='active').count()
    total_sales = TicketSale.objects.filter(provider=provider).count()
    total_revenue = TicketSale.objects.filter(provider=provider).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Recent activity
    recent_tickets = Ticket.objects.filter(provider=provider).order_by('-created_at')[:10]
    recent_sales = TicketSale.objects.filter(provider=provider).order_by('-sold_at')[:10]
    
    # Subscription info
    current_subscription = ProviderSubscription.objects.filter(
        provider=provider,
        status='active'
    ).first()
    
    context = {
        'page_title': f'Provider - {provider.business_name}',
        'provider': provider,
        'total_tickets': total_tickets,
        'active_tickets': active_tickets,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'recent_tickets': recent_tickets,
        'recent_sales': recent_sales,
        'current_subscription': current_subscription,
    }
    
    return render(request, 'super_admin/provider_detail.html', context)


@login_required
@user_passes_test(is_super_admin)
def approve_provider(request, provider_id):
    """Approve a provider"""
    provider = get_object_or_404(Provider, id=provider_id)
    
    if request.method == 'POST':
        provider.status = 'active'
        provider.is_approved = True
        provider.approved_by = request.user
        provider.approved_at = timezone.now()
        provider.save()
        
        messages.success(request, f'Provider {provider.business_name} has been approved.')
        return redirect('super_admin:provider_detail', provider_id=provider.id)
    
    return render(request, 'super_admin/approve_provider.html', {
        'provider': provider
    })


@login_required
@user_passes_test(is_super_admin)
def suspend_provider(request, provider_id):
    """Suspend a provider"""
    provider = get_object_or_404(Provider, id=provider_id)
    
    if request.method == 'POST':
        provider.status = 'suspended'
        provider.save()
        
        messages.success(request, f'Provider {provider.business_name} has been suspended.')
        return redirect('super_admin:provider_detail', provider_id=provider.id)
    
    return render(request, 'super_admin/suspend_provider.html', {
        'provider': provider
    })


@login_required
@user_passes_test(is_super_admin)
def analytics_view(request):
    """Platform analytics"""
    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Daily analytics
    daily_analytics = PlatformAnalytics.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Provider growth
    provider_growth = Provider.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(count=Count('id'))
    
    # Revenue trends
    revenue_trends = TicketSale.objects.filter(
        sold_at__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(sold_at)'}
    ).values('day').annotate(
        revenue=Sum('total_amount'),
        sales_count=Count('id')
    )
    
    context = {
        'page_title': 'Platform Analytics',
        'daily_analytics': daily_analytics,
        'provider_growth': provider_growth,
        'revenue_trends': revenue_trends,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'super_admin/analytics.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_global_stats(request):
    """API endpoint for global statistics"""
    if not is_super_admin(request.user):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get statistics
    stats = {
        'total_providers': Provider.objects.count(),
        'active_providers': Provider.objects.filter(status='active').count(),
        'total_tickets': Ticket.objects.count(),
        'active_tickets': Ticket.objects.filter(status='active').count(),
        'total_revenue': TicketSale.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'monthly_revenue': TicketSale.objects.filter(
            sold_at__gte=timezone.now() - timedelta(days=30)
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_provider_stats(request, provider_id):
    """API endpoint for provider statistics"""
    if not is_super_admin(request.user):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        provider = Provider.objects.get(id=provider_id)
    except Provider.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)
    
    stats = {
        'provider_name': provider.business_name,
        'total_tickets': Ticket.objects.filter(provider=provider).count(),
        'active_tickets': Ticket.objects.filter(provider=provider, status='active').count(),
        'total_sales': TicketSale.objects.filter(provider=provider).count(),
        'total_revenue': TicketSale.objects.filter(provider=provider).aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'subscription_status': provider.get_subscription_status(),
    }
    
    return Response(stats)

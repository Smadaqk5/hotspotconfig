from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
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
from config_generator.models import GeneratedConfig


def is_provider(user):
    """Check if user is a provider"""
    return user.is_authenticated and (user.user_type == 'provider' or user.is_superuser)


@login_required
@user_passes_test(is_provider)
def provider_dashboard(request):
    """Provider Dashboard"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get current subscription
    current_subscription = ProviderSubscription.objects.filter(
        provider=provider,
        status='active'
    ).first()
    
    # Provider statistics
    total_tickets = Ticket.objects.filter(provider=provider).count()
    active_tickets = Ticket.objects.filter(provider=provider, status='active').count()
    used_tickets = Ticket.objects.filter(provider=provider, status='used').count()
    expired_tickets = Ticket.objects.filter(provider=provider, status='expired').count()
    
    # Sales statistics
    total_sales = TicketSale.objects.filter(provider=provider).count()
    total_revenue = TicketSale.objects.filter(provider=provider).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Monthly statistics
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_tickets = Ticket.objects.filter(
        provider=provider,
        created_at__gte=month_start
    ).count()
    monthly_sales = TicketSale.objects.filter(
        provider=provider,
        sold_at__gte=month_start
    ).count()
    monthly_revenue = TicketSale.objects.filter(
        provider=provider,
        sold_at__gte=month_start
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Recent activity
    recent_tickets = Ticket.objects.filter(provider=provider).order_by('-created_at')[:10]
    recent_sales = TicketSale.objects.filter(provider=provider).order_by('-sold_at')[:10]
    
    # Ticket types
    ticket_types = TicketType.objects.filter(provider=provider, is_active=True)
    
    # End users
    total_end_users = EndUser.objects.filter(provider=provider).count()
    active_end_users = EndUser.objects.filter(provider=provider, is_active=True).count()
    
    context = {
        'page_title': 'Provider Dashboard',
        'provider': provider,
        'current_subscription': current_subscription,
        'total_tickets': total_tickets,
        'active_tickets': active_tickets,
        'used_tickets': used_tickets,
        'expired_tickets': expired_tickets,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'monthly_tickets': monthly_tickets,
        'monthly_sales': monthly_sales,
        'monthly_revenue': monthly_revenue,
        'recent_tickets': recent_tickets,
        'recent_sales': recent_sales,
        'ticket_types': ticket_types,
        'total_end_users': total_end_users,
        'active_end_users': active_end_users,
    }
    
    return render(request, 'provider/dashboard.html', context)


@login_required
@user_passes_test(is_provider)
def ticket_management(request):
    """Ticket management page"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get tickets with filters
    tickets = Ticket.objects.filter(provider=provider).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Filter by ticket type
    type_filter = request.GET.get('type')
    if type_filter:
        tickets = tickets.filter(ticket_type_id=type_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        tickets = tickets.filter(
            Q(code__icontains=search) |
            Q(username__icontains=search)
        )
    
    # Get ticket types for filter
    ticket_types = TicketType.objects.filter(provider=provider, is_active=True)
    
    context = {
        'page_title': 'Ticket Management',
        'tickets': tickets,
        'ticket_types': ticket_types,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search': search,
    }
    
    return render(request, 'provider/ticket_management.html', context)


@login_required
@user_passes_test(is_provider)
def generate_tickets(request):
    """Generate new tickets"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Check subscription
    current_subscription = ProviderSubscription.objects.filter(
        provider=provider,
        status='active'
    ).first()
    
    if not current_subscription or not current_subscription.is_active():
        messages.error(request, 'Active subscription required to generate tickets.')
        return redirect('provider:subscription')
    
    if request.method == 'POST':
        ticket_type_id = request.POST.get('ticket_type')
        quantity = int(request.POST.get('quantity', 1))
        batch_name = request.POST.get('batch_name', '')
        
        try:
            ticket_type = TicketType.objects.get(id=ticket_type_id, provider=provider)
        except TicketType.DoesNotExist:
            messages.error(request, 'Invalid ticket type.')
            return redirect('provider:generate_tickets')
        
        # Check if provider can generate more tickets
        if not current_subscription.can_generate_tickets(quantity):
            messages.error(request, f'Cannot generate {quantity} tickets. Subscription limit reached.')
            return redirect('provider:generate_tickets')
        
        # Create ticket batch
        batch = TicketBatch.objects.create(
            provider=provider,
            ticket_type=ticket_type,
            batch_name=batch_name or f"Batch {timezone.now().strftime('%Y%m%d_%H%M%S')}",
            quantity=quantity,
            generated_by=request.user
        )
        
        # Generate tickets
        generated_tickets = []
        for i in range(quantity):
            ticket = Ticket.objects.create(
                provider=provider,
                ticket_type=ticket_type,
                price=ticket_type.price,
                max_time=ticket_type.value * 60 if ticket_type.ticket_type == 'time' else 0,
                max_data=ticket_type.value * 1024 if ticket_type.ticket_type == 'data' else 0,
                expires_at=timezone.now() + timedelta(days=30)
            )
            generated_tickets.append(ticket)
        
        messages.success(request, f'Successfully generated {quantity} tickets.')
        return redirect('provider:ticket_management')
    
    # Get available ticket types
    ticket_types = TicketType.objects.filter(provider=provider, is_active=True)
    
    context = {
        'page_title': 'Generate Tickets',
        'ticket_types': ticket_types,
        'current_subscription': current_subscription,
    }
    
    return render(request, 'provider/generate_tickets.html', context)


@login_required
@user_passes_test(is_provider)
def sales_analytics(request):
    """Sales analytics and reporting"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Daily sales
    daily_sales = TicketSale.objects.filter(
        provider=provider,
        sold_at__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(sold_at)'}
    ).values('day').annotate(
        sales_count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('day')
    
    # Ticket type performance
    ticket_type_performance = TicketSale.objects.filter(
        provider=provider,
        sold_at__date__range=[start_date, end_date]
    ).values('ticket__ticket_type__name').annotate(
        sales_count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('-revenue')
    
    # Monthly comparison
    current_month = TicketSale.objects.filter(
        provider=provider,
        sold_at__date__gte=end_date.replace(day=1)
    ).aggregate(
        sales_count=Count('id'),
        revenue=Sum('total_amount')
    )
    
    previous_month = TicketSale.objects.filter(
        provider=provider,
        sold_at__date__gte=(end_date.replace(day=1) - timedelta(days=1)).replace(day=1),
        sold_at__date__lt=end_date.replace(day=1)
    ).aggregate(
        sales_count=Count('id'),
        revenue=Sum('total_amount')
    )
    
    context = {
        'page_title': 'Sales Analytics',
        'daily_sales': daily_sales,
        'ticket_type_performance': ticket_type_performance,
        'current_month': current_month,
        'previous_month': previous_month,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'provider/sales_analytics.html', context)


@login_required
@user_passes_test(is_provider)
def end_users_management(request):
    """Manage end users"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    end_users = EndUser.objects.filter(provider=provider).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        end_users = end_users.filter(is_active=True)
    elif status_filter == 'inactive':
        end_users = end_users.filter(is_active=False)
    
    # Search
    search = request.GET.get('search')
    if search:
        end_users = end_users.filter(username__icontains=search)
    
    context = {
        'page_title': 'End Users Management',
        'end_users': end_users,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'provider/end_users_management.html', context)


@login_required
@user_passes_test(is_provider)
def subscription_management(request):
    """Subscription management"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get current subscription
    current_subscription = ProviderSubscription.objects.filter(
        provider=provider,
        status='active'
    ).first()
    
    # Get subscription history
    subscription_history = ProviderSubscription.objects.filter(
        provider=provider
    ).order_by('-created_at')
    
    # Get available plans
    available_plans = ProviderSubscriptionPlan.objects.filter(is_active=True)
    
    context = {
        'page_title': 'Subscription Management',
        'current_subscription': current_subscription,
        'subscription_history': subscription_history,
        'available_plans': available_plans,
    }
    
    return render(request, 'provider/subscription_management.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_provider_stats(request):
    """API endpoint for provider statistics"""
    if not is_provider(request.user):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        return Response({'error': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get statistics
    stats = {
        'total_tickets': Ticket.objects.filter(provider=provider).count(),
        'active_tickets': Ticket.objects.filter(provider=provider, status='active').count(),
        'total_sales': TicketSale.objects.filter(provider=provider).count(),
        'total_revenue': TicketSale.objects.filter(provider=provider).aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'monthly_revenue': TicketSale.objects.filter(
            provider=provider,
            sold_at__gte=timezone.now() - timedelta(days=30)
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
    }
    
    return Response(stats)


@login_required
@user_passes_test(is_provider)
def view_tickets(request):
    """View all tickets for the provider"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get tickets with filters
    tickets = Ticket.objects.filter(provider=provider).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Filter by ticket type
    type_filter = request.GET.get('type')
    if type_filter:
        tickets = tickets.filter(ticket_type_id=type_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        tickets = tickets.filter(
            Q(code__icontains=search) |
            Q(username__icontains=search)
        )
    
    # Get ticket types for filter
    ticket_types = TicketType.objects.filter(provider=provider, is_active=True)
    
    context = {
        'page_title': 'View Tickets',
        'tickets': tickets,
        'ticket_types': ticket_types,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search': search,
    }
    
    return render(request, 'provider/view_tickets.html', context)


@login_required
@user_passes_test(is_provider)
def download_config(request):
    """Download MikroTik configuration"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get the latest generated config for this provider
    config = GeneratedConfig.objects.filter(provider=provider).order_by('-created_at').first()
    
    if not config:
        messages.error(request, 'No configuration found. Please generate a configuration first.')
        return redirect('provider:dashboard')
    
    # Create HTTP response with the config file
    response = HttpResponse(config.config_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="mikrotik_config_{provider.business_name}_{timezone.now().strftime("%Y%m%d")}.rsc"'
    
    return response

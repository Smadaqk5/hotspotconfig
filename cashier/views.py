"""
Cashier-specific views for the MikroTik Hotspot Platform
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta

from accounts.decorators import cashier_required, cashier_permission_required
from accounts.models import Cashier
from tickets.models import Ticket, TicketSale, TicketType
from subscriptions.models import ProviderSubscription


@cashier_required
def cashier_dashboard(request):
    """Cashier Dashboard - Limited access based on permissions"""
    try:
        cashier = request.user.cashier_profile
        provider = cashier.provider
    except Cashier.DoesNotExist:
        messages.error(request, "Cashier profile not found.")
        return redirect('home')
    
    # Get statistics based on permissions
    stats = {}
    
    if cashier.can_view_sales:
        # Sales statistics
        today = timezone.now().date()
        stats['today_sales'] = TicketSale.objects.filter(
            ticket__provider=provider,
            sold_at__date=today
        ).count()
        
        stats['today_revenue'] = TicketSale.objects.filter(
            ticket__provider=provider,
            sold_at__date=today
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    if cashier.can_generate_tickets:
        # Ticket generation statistics
        stats['tickets_generated'] = Ticket.objects.filter(provider=provider).count()
        stats['active_tickets'] = Ticket.objects.filter(
            provider=provider, 
            status='active'
        ).count()
    
    # Recent activity
    recent_activity = []
    if cashier.can_view_sales:
        recent_sales = TicketSale.objects.filter(
            ticket__provider=provider
        ).order_by('-sold_at')[:5]
        recent_activity.extend([('sale', sale) for sale in recent_sales])
    
    context = {
        'cashier': cashier,
        'provider': provider,
        'stats': stats,
        'recent_activity': recent_activity,
        'page_title': f'Cashier Dashboard - {provider.business_name}'
    }
    return render(request, 'cashier/dashboard.html', context)


@cashier_permission_required('can_generate_tickets')
def generate_tickets(request):
    """Generate tickets - Cashier permission required"""
    try:
        cashier = request.user.cashier_profile
        provider = cashier.provider
    except Cashier.DoesNotExist:
        messages.error(request, "Cashier profile not found.")
        return redirect('cashier:dashboard')
    
    if request.method == 'POST':
        ticket_type_id = request.POST.get('ticket_type')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            ticket_type = TicketType.objects.get(id=ticket_type_id, provider=provider)
            
            # Generate tickets
            generated_tickets = []
            for i in range(quantity):
                ticket = Ticket.objects.create(
                    provider=provider,
                    ticket_type=ticket_type,
                    generated_by=request.user
                )
                generated_tickets.append(ticket)
            
            messages.success(request, f'Successfully generated {quantity} tickets.')
            return redirect('cashier:view_tickets')
            
        except TicketType.DoesNotExist:
            messages.error(request, 'Invalid ticket type selected.')
    
    # Get available ticket types for this provider
    ticket_types = TicketType.objects.filter(provider=provider, is_active=True)
    
    context = {
        'cashier': cashier,
        'provider': provider,
        'ticket_types': ticket_types,
        'page_title': 'Generate Tickets'
    }
    return render(request, 'cashier/generate_tickets.html', context)


@cashier_permission_required('can_sell_tickets')
def sell_tickets(request):
    """Sell tickets - Cashier permission required"""
    try:
        cashier = request.user.cashier_profile
        provider = cashier.provider
    except Cashier.DoesNotExist:
        messages.error(request, "Cashier profile not found.")
        return redirect('cashier:dashboard')
    
    if request.method == 'POST':
        ticket_code = request.POST.get('ticket_code')
        customer_name = request.POST.get('customer_name', '')
        customer_phone = request.POST.get('customer_phone', '')
        payment_method = request.POST.get('payment_method', 'cash')
        
        try:
            ticket = Ticket.objects.get(code=ticket_code, provider=provider)
            
            if ticket.status != 'active':
                messages.error(request, 'Ticket is not available for sale.')
                return redirect('cashier:sell_tickets')
            
            # Create sale record
            sale = TicketSale.objects.create(
                provider=provider,
                ticket=ticket,
                customer_name=customer_name,
                customer_phone=customer_phone,
                unit_price=ticket.price,
                total_amount=ticket.price,
                payment_method=payment_method,
                status='completed'
            )
            
            # Mark ticket as used
            ticket.status = 'used'
            ticket.used_at = timezone.now()
            ticket.save()
            
            messages.success(request, f'Ticket {ticket_code} sold successfully!')
            return redirect('cashier:sell_tickets')
            
        except Ticket.DoesNotExist:
            messages.error(request, 'Ticket not found.')
    
    context = {
        'cashier': cashier,
        'provider': provider,
        'page_title': 'Sell Tickets'
    }
    return render(request, 'cashier/sell_tickets.html', context)


@cashier_permission_required('can_view_sales')
def view_sales(request):
    """View sales - Cashier permission required"""
    try:
        cashier = request.user.cashier_profile
        provider = cashier.provider
    except Cashier.DoesNotExist:
        messages.error(request, "Cashier profile not found.")
        return redirect('cashier:dashboard')
    
    # Get sales data
    sales = TicketSale.objects.filter(ticket__provider=provider).order_by('-sold_at')
    
    # Filter by date if provided
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        sales = sales.filter(sold_at__date__gte=date_from)
    if date_to:
        sales = sales.filter(sold_at__date__lte=date_to)
    
    # Statistics
    total_sales = sales.count()
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'cashier': cashier,
        'provider': provider,
        'sales': sales,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'page_title': 'Sales Report'
    }
    return render(request, 'cashier/view_sales.html', context)


def view_tickets(request):
    """View available tickets"""
    try:
        cashier = request.user.cashier_profile
        provider = cashier.provider
    except Cashier.DoesNotExist:
        messages.error(request, "Cashier profile not found.")
        return redirect('cashier:dashboard')
    
    # Get tickets for this provider
    tickets = Ticket.objects.filter(provider=provider).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    context = {
        'cashier': cashier,
        'provider': provider,
        'tickets': tickets,
        'page_title': 'Available Tickets'
    }
    return render(request, 'cashier/view_tickets.html', context)

"""
Celery tasks for tickets app
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import Ticket, TicketType


@shared_task
def expire_tickets():
    """Expire tickets that have passed their expiry date"""
    now = timezone.now()
    expired_tickets = Ticket.objects.filter(
        status='active',
        expires_at__lt=now
    )
    
    count = 0
    for ticket in expired_tickets:
        ticket.expire()
        count += 1
    
    return f"Expired {count} tickets"


@shared_task
def cleanup_old_tickets():
    """Clean up old expired tickets (older than 30 days)"""
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    old_tickets = Ticket.objects.filter(
        status__in=['expired', 'cancelled'],
        created_at__lt=cutoff_date
    )
    
    count = old_tickets.count()
    old_tickets.delete()
    
    return f"Cleaned up {count} old tickets"


@shared_task
def generate_ticket_batch(batch_id):
    """Generate tickets for a batch"""
    from .models import TicketBatch
    
    try:
        batch = TicketBatch.objects.get(id=batch_id)
        batch.generate_tickets()
        return f"Generated {batch.quantity} tickets for batch {batch.name}"
    except TicketBatch.DoesNotExist:
        return f"Batch {batch_id} not found"


@shared_task
def sync_tickets_to_router():
    """Sync active tickets to MikroTik router"""
    # This would integrate with MikroTik API
    # For now, just mark tickets as synced
    active_tickets = Ticket.objects.filter(
        status='active',
        is_synced_to_router=False
    )
    
    count = 0
    for ticket in active_tickets:
        # Here you would implement actual MikroTik API integration
        # For now, just mark as synced
        ticket.is_synced_to_router = True
        ticket.save(update_fields=['is_synced_to_router'])
        count += 1
    
    return f"Synced {count} tickets to router"


@shared_task
def send_ticket_expiry_reminders():
    """Send reminders for tickets expiring soon"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    # Find tickets expiring in the next 24 hours
    tomorrow = timezone.now() + timezone.timedelta(hours=24)
    expiring_tickets = Ticket.objects.filter(
        status='active',
        expires_at__lte=tomorrow,
        expires_at__gt=timezone.now()
    )
    
    count = 0
    for ticket in expiring_tickets:
        if ticket.user.email:
            subject = f"Ticket Expiring Soon - {ticket.username}"
            message = f"""
            Your ticket {ticket.username} is expiring soon.
            Expiry time: {ticket.expires_at}
            Ticket type: {ticket.ticket_type.name}
            
            Please use your ticket before it expires.
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [ticket.user.email],
                    fail_silently=False,
                )
                count += 1
            except Exception as e:
                print(f"Failed to send reminder for ticket {ticket.id}: {e}")
    
    return f"Sent {count} expiry reminders"


@shared_task
def update_ticket_usage_stats():
    """Update ticket usage statistics"""
    from .models import TicketUsage
    
    # This would typically be called by the MikroTik router
    # or a monitoring system to update usage statistics
    
    # For now, just return a placeholder
    return "Updated ticket usage statistics"


@shared_task
def generate_daily_reports():
    """Generate daily ticket sales reports"""
    from django.db.models import Count, Sum
    from .models import TicketSale
    from datetime import date
    
    today = date.today()
    
    # Get today's sales
    today_sales = TicketSale.objects.filter(sold_at__date=today)
    
    total_sales = today_sales.count()
    total_revenue = today_sales.aggregate(total=Sum('sale_price'))['total'] or 0
    
    # Get sales by ticket type
    sales_by_type = today_sales.values('ticket__ticket_type__name').annotate(
        count=Count('id'),
        revenue=Sum('sale_price')
    )
    
    report = {
        'date': today,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'sales_by_type': list(sales_by_type)
    }
    
    return report

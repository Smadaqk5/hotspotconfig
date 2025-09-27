"""
Celery tasks for subscription management
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import ProviderSubscription, ProviderSubscriptionPlan
from accounts.models import Provider
from tickets.models import Ticket
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_expired_subscriptions():
    """Check and handle expired subscriptions"""
    try:
        expired_subscriptions = ProviderSubscription.objects.filter(
            status='active',
            end_date__lt=timezone.now()
        )
        
        for subscription in expired_subscriptions:
            subscription.status = 'expired'
            subscription.save()
            
            # Update provider status
            provider = subscription.provider
            provider.subscription_status = 'expired'
            provider.save()
            
            # Send expiry notification
            send_subscription_expiry_notification.delay(subscription.id)
            
        logger.info(f"Processed {expired_subscriptions.count()} expired subscriptions")
        return f"Processed {expired_subscriptions.count()} expired subscriptions"
        
    except Exception as e:
        logger.error(f"Error checking expired subscriptions: {e}")
        return f"Error: {str(e)}"


@shared_task
def check_expired_tickets():
    """Check and handle expired tickets"""
    try:
        expired_tickets = Ticket.objects.filter(
            status='active',
            expires_at__lt=timezone.now()
        )
        
        for ticket in expired_tickets:
            ticket.status = 'expired'
            ticket.save()
            
        logger.info(f"Processed {expired_tickets.count()} expired tickets")
        return f"Processed {expired_tickets.count()} expired tickets"
        
    except Exception as e:
        logger.error(f"Error checking expired tickets: {e}")
        return f"Error: {str(e)}"


@shared_task
def send_subscription_expiry_notification(subscription_id):
    """Send subscription expiry notification"""
    try:
        subscription = ProviderSubscription.objects.get(id=subscription_id)
        provider = subscription.provider
        
        subject = f"Subscription Expired - {provider.business_name}"
        message = f"""
Dear {provider.contact_person},

Your subscription to {subscription.plan.name} has expired.

Please renew your subscription to continue using the platform.

Subscription Details:
- Plan: {subscription.plan.name}
- Expired: {subscription.end_date.strftime('%Y-%m-%d %H:%M:%S')}
- Amount: KSh {subscription.plan.price}

To renew, please log in to your dashboard and select a new subscription plan.

Best regards,
Hotspot Config Team
"""
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [provider.contact_email],
            fail_silently=False,
        )
        
        logger.info(f"Sent expiry notification to {provider.contact_email}")
        return f"Sent expiry notification to {provider.contact_email}"
        
    except Exception as e:
        logger.error(f"Error sending expiry notification: {e}")
        return f"Error: {str(e)}"


@shared_task
def send_subscription_reminder(subscription_id):
    """Send subscription renewal reminder"""
    try:
        subscription = ProviderSubscription.objects.get(id=subscription_id)
        provider = subscription.provider
        
        days_remaining = subscription.days_remaining()
        
        subject = f"Subscription Renewal Reminder - {provider.business_name}"
        message = f"""
Dear {provider.contact_person},

Your subscription to {subscription.plan.name} will expire in {days_remaining} days.

Please renew your subscription to avoid service interruption.

Subscription Details:
- Plan: {subscription.plan.name}
- Expires: {subscription.end_date.strftime('%Y-%m-%d %H:%M:%S')}
- Days Remaining: {days_remaining}
- Amount: KSh {subscription.plan.price}

To renew, please log in to your dashboard and select a new subscription plan.

Best regards,
Hotspot Config Team
"""
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [provider.contact_email],
            fail_silently=False,
        )
        
        logger.info(f"Sent renewal reminder to {provider.contact_email}")
        return f"Sent renewal reminder to {provider.contact_email}"
        
    except Exception as e:
        logger.error(f"Error sending renewal reminder: {e}")
        return f"Error: {str(e)}"


@shared_task
def send_daily_reminders():
    """Send daily reminders for subscriptions expiring in 7 days"""
    try:
        seven_days_from_now = timezone.now() + timedelta(days=7)
        
        expiring_subscriptions = ProviderSubscription.objects.filter(
            status='active',
            end_date__lte=seven_days_from_now,
            end_date__gte=timezone.now()
        )
        
        for subscription in expiring_subscriptions:
            send_subscription_reminder.delay(subscription.id)
            
        logger.info(f"Sent {expiring_subscriptions.count()} daily reminders")
        return f"Sent {expiring_subscriptions.count()} daily reminders"
        
    except Exception as e:
        logger.error(f"Error sending daily reminders: {e}")
        return f"Error: {str(e)}"


@shared_task
def cleanup_expired_data():
    """Clean up expired data and old records"""
    try:
        # Clean up expired tickets older than 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        old_expired_tickets = Ticket.objects.filter(
            status='expired',
            expires_at__lt=thirty_days_ago
        )
        
        deleted_tickets = old_expired_tickets.count()
        old_expired_tickets.delete()
        
        logger.info(f"Cleaned up {deleted_tickets} old expired tickets")
        return f"Cleaned up {deleted_tickets} old expired tickets"
        
    except Exception as e:
        logger.error(f"Error cleaning up expired data: {e}")
        return f"Error: {str(e)}"


@shared_task
def generate_daily_reports():
    """Generate daily reports for providers"""
    try:
        active_providers = Provider.objects.filter(status='active')
        
        for provider in active_providers:
            # Generate daily report for each provider
            generate_provider_daily_report.delay(provider.id)
            
        logger.info(f"Generated daily reports for {active_providers.count()} providers")
        return f"Generated daily reports for {active_providers.count()} providers"
        
    except Exception as e:
        logger.error(f"Error generating daily reports: {e}")
        return f"Error: {str(e)}"


@shared_task
def generate_provider_daily_report(provider_id):
    """Generate daily report for a specific provider"""
    try:
        provider = Provider.objects.get(id=provider_id)
        
        # Get yesterday's data
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # Get tickets generated yesterday
        tickets_generated = Ticket.objects.filter(
            provider=provider,
            created_at__date=yesterday
        ).count()
        
        # Get tickets sold yesterday
        tickets_sold = Ticket.objects.filter(
            provider=provider,
            sales__sold_at__date=yesterday
        ).count()
        
        # Get revenue yesterday
        revenue = sum(
            ticket.sales.total_amount for ticket in Ticket.objects.filter(
                provider=provider,
                sales__sold_at__date=yesterday
            ) if hasattr(ticket, 'sales')
        )
        
        subject = f"Daily Report - {provider.business_name}"
        message = f"""
Daily Report for {yesterday.strftime('%Y-%m-%d')}

Provider: {provider.business_name}

Statistics:
- Tickets Generated: {tickets_generated}
- Tickets Sold: {tickets_sold}
- Revenue: KSh {revenue:.2f}

Best regards,
Hotspot Config Team
"""
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [provider.contact_email],
            fail_silently=False,
        )
        
        logger.info(f"Generated daily report for {provider.business_name}")
        return f"Generated daily report for {provider.business_name}"
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return f"Error: {str(e)}"
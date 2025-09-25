"""
Background tasks for subscription management
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Subscription, SubscriptionUsage
from accounts.models import User
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_expired_subscriptions():
    """Check for expired subscriptions and update their status"""
    try:
        expired_subscriptions = Subscription.objects.filter(
            is_active=True,
            status='active',
            end_date__lt=timezone.now()
        )
        
        count = 0
        for subscription in expired_subscriptions:
            subscription.status = 'expired'
            subscription.is_active = False
            subscription.save()
            count += 1
            
            # Send expiration notification email
            send_subscription_expired_email.delay(subscription.id)
        
        logger.info(f"Marked {count} subscriptions as expired")
        return f"Processed {count} expired subscriptions"
        
    except Exception as e:
        logger.error(f"Error checking expired subscriptions: {e}")
        return f"Error: {str(e)}"


@shared_task
def send_renewal_reminders():
    """Send renewal reminder emails to users with expiring subscriptions"""
    try:
        # Find subscriptions expiring in 7 days
        reminder_date = timezone.now() + timedelta(days=7)
        expiring_subscriptions = Subscription.objects.filter(
            is_active=True,
            status='active',
            end_date__lte=reminder_date,
            end_date__gt=timezone.now()
        )
        
        count = 0
        for subscription in expiring_subscriptions:
            send_renewal_reminder_email.delay(subscription.id)
            count += 1
        
        logger.info(f"Sent {count} renewal reminder emails")
        return f"Sent {count} renewal reminders"
        
    except Exception as e:
        logger.error(f"Error sending renewal reminders: {e}")
        return f"Error: {str(e)}"


@shared_task
def send_subscription_expired_email(subscription_id):
    """Send email notification when subscription expires"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        user = subscription.user
        
        subject = 'Your Hotspot Config Subscription Has Expired'
        message = f"""
        Dear {user.first_name or user.username},
        
        Your subscription to {subscription.plan.name} has expired.
        
        To continue generating MikroTik configurations, please renew your subscription.
        
        Visit our website to renew: {settings.FRONTEND_URL}/pricing
        
        Best regards,
        Hotspot Config Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent expiration email to {user.email}")
        return f"Expiration email sent to {user.email}"
        
    except Exception as e:
        logger.error(f"Error sending expiration email: {e}")
        return f"Error: {str(e)}"


@shared_task
def send_renewal_reminder_email(subscription_id):
    """Send renewal reminder email"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        user = subscription.user
        days_remaining = subscription.days_remaining()
        
        subject = f'Your Hotspot Config Subscription Expires in {days_remaining} Days'
        message = f"""
        Dear {user.first_name or user.username},
        
        Your subscription to {subscription.plan.name} will expire in {days_remaining} days.
        
        To avoid service interruption, please renew your subscription before it expires.
        
        Visit our website to renew: {settings.FRONTEND_URL}/pricing
        
        Best regards,
        Hotspot Config Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent renewal reminder to {user.email}")
        return f"Renewal reminder sent to {user.email}"
        
    except Exception as e:
        logger.error(f"Error sending renewal reminder: {e}")
        return f"Error: {str(e)}"


@shared_task
def cleanup_old_data():
    """Clean up old data to keep database size manageable"""
    try:
        from datetime import timedelta
        
        # Delete old expired subscriptions (older than 1 year)
        cutoff_date = timezone.now() - timedelta(days=365)
        old_subscriptions = Subscription.objects.filter(
            status='expired',
            end_date__lt=cutoff_date
        )
        
        count = old_subscriptions.count()
        old_subscriptions.delete()
        
        logger.info(f"Cleaned up {count} old expired subscriptions")
        return f"Cleaned up {count} old subscriptions"
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return f"Error: {str(e)}"

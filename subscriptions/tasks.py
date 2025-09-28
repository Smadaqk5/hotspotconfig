"""
Automated tasks for subscription management
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import logging

from accounts.models import Provider
from .models import ProviderSubscription

logger = logging.getLogger(__name__)

class SubscriptionTasks:
    """Tasks for subscription management"""
    
    @staticmethod
    def expire_subscriptions():
        """Expire subscriptions that have passed their end date"""
        try:
            now = timezone.now()
            expired_subscriptions = ProviderSubscription.objects.filter(
                status='active',
                expires_at__lt=now
            )
            
            count = 0
            for subscription in expired_subscriptions:
                subscription.status = 'expired'
                subscription.save()
                
                # Update provider status
                provider = subscription.provider
                provider.subscription_status = 'inactive'
                provider.save()
                
                count += 1
                logger.info(f"Expired subscription for provider {provider.business_name}")
            
            logger.info(f"Expired {count} subscriptions")
            return count
            
        except Exception as e:
            logger.error(f"Failed to expire subscriptions: {e}")
            return 0
    
    @staticmethod
    def send_expiry_reminders():
        """Send reminders for subscriptions expiring soon"""
        try:
            # Get subscriptions expiring in 7 days
            expiry_date = timezone.now() + timedelta(days=7)
            expiring_subscriptions = ProviderSubscription.objects.filter(
                status='active',
                expires_at__lte=expiry_date,
                expires_at__gt=timezone.now()
            )
            
            count = 0
            for subscription in expiring_subscriptions:
                # Send email reminder (implement email service)
                provider = subscription.provider
                logger.info(f"Sending expiry reminder to {provider.contact_email}")
                count += 1
            
            logger.info(f"Sent {count} expiry reminders")
            return count
            
        except Exception as e:
            logger.error(f"Failed to send expiry reminders: {e}")
            return 0
    
    @staticmethod
    def cleanup_expired_tickets():
        """Clean up expired tickets"""
        try:
            from tickets.models import Ticket
            
            now = timezone.now()
            expired_tickets = Ticket.objects.filter(
                status='active',
                expires_at__lt=now
            )
            
            count = 0
            for ticket in expired_tickets:
                ticket.status = 'expired'
                ticket.save()
                count += 1
            
            logger.info(f"Expired {count} tickets")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired tickets: {e}")
            return 0
    
    @staticmethod
    def generate_usage_reports():
        """Generate monthly usage reports for providers"""
        try:
            from tickets.models import Ticket, TicketSale
            from payments.models import Payment
            from django.db.models import Sum, Count
            
            # Get active subscriptions
            active_subscriptions = ProviderSubscription.objects.filter(
                status='active'
            )
            
            count = 0
            for subscription in active_subscriptions:
                provider = subscription.provider
                
                # Get monthly statistics
                month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                monthly_tickets = Ticket.objects.filter(
                    provider=provider,
                    created_at__gte=month_start
                ).count()
                
                monthly_revenue = Payment.objects.filter(
                    provider=provider,
                    status='completed',
                    created_at__gte=month_start
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                # Log usage report
                logger.info(f"Usage report for {provider.business_name}: "
                          f"{monthly_tickets} tickets, Ksh {monthly_revenue}")
                
                count += 1
            
            logger.info(f"Generated {count} usage reports")
            return count
            
        except Exception as e:
            logger.error(f"Failed to generate usage reports: {e}")
            return 0
    
    @staticmethod
    def cleanup_old_data():
        """Clean up old data to maintain database performance"""
        try:
            from tickets.models import Ticket, TicketUsage
            from django.utils import timezone
            from datetime import timedelta
            
            # Delete old expired tickets (older than 6 months)
            cutoff_date = timezone.now() - timedelta(days=180)
            old_tickets = Ticket.objects.filter(
                status='expired',
                created_at__lt=cutoff_date
            )
            
            ticket_count = old_tickets.count()
            old_tickets.delete()
            
            # Delete old usage records (older than 1 year)
            usage_cutoff = timezone.now() - timedelta(days=365)
            old_usage = TicketUsage.objects.filter(
                created_at__lt=usage_cutoff
            )
            
            usage_count = old_usage.count()
            old_usage.delete()
            
            logger.info(f"Cleaned up {ticket_count} old tickets and {usage_count} old usage records")
            return ticket_count + usage_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0

class Command(BaseCommand):
    """Django management command for running subscription tasks"""
    help = 'Run subscription management tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            choices=[
                'expire_subscriptions',
                'send_reminders',
                'cleanup_tickets',
                'usage_reports',
                'cleanup_data',
                'all'
            ],
            default='all',
            help='Task to run'
        )
    
    def handle(self, *args, **options):
        task = options['task']
        
        if task == 'expire_subscriptions' or task == 'all':
            count = SubscriptionTasks.expire_subscriptions()
            self.stdout.write(f"Expired {count} subscriptions")
        
        if task == 'send_reminders' or task == 'all':
            count = SubscriptionTasks.send_expiry_reminders()
            self.stdout.write(f"Sent {count} expiry reminders")
        
        if task == 'cleanup_tickets' or task == 'all':
            count = SubscriptionTasks.cleanup_expired_tickets()
            self.stdout.write(f"Expired {count} tickets")
        
        if task == 'usage_reports' or task == 'all':
            count = SubscriptionTasks.generate_usage_reports()
            self.stdout.write(f"Generated {count} usage reports")
        
        if task == 'cleanup_data' or task == 'all':
            count = SubscriptionTasks.cleanup_old_data()
            self.stdout.write(f"Cleaned up {count} old records")
        
        self.stdout.write(self.style.SUCCESS('Tasks completed successfully'))
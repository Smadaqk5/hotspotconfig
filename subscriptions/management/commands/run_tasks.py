"""
Management command for running subscription tasks
"""
from django.core.management.base import BaseCommand
from subscriptions.tasks import SubscriptionTasks

class Command(BaseCommand):
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

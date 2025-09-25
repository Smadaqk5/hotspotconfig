"""
Management command to create sample ticket types
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tickets.models import TicketType

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample ticket types for the ticketing system'

    def handle(self, *args, **options):
        # Get existing admin user
        try:
            admin_user = User.objects.get(email='admin@hotspotconfig.com')
        except User.DoesNotExist:
            # Fallback to any superuser
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()

        # Sample ticket types
        ticket_types = [
            {
                'name': '1 Hour WiFi',
                'ticket_type': 'time',
                'description': '1 hour of internet access',
                'duration_hours': 1,
                'price': 50.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 1
            },
            {
                'name': '2 Hours WiFi',
                'ticket_type': 'time',
                'description': '2 hours of internet access',
                'duration_hours': 2,
                'price': 80.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 2
            },
            {
                'name': '1 Day WiFi',
                'ticket_type': 'time',
                'description': '24 hours of internet access',
                'duration_hours': 24,
                'price': 200.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 3
            },
            {
                'name': '1GB Data',
                'ticket_type': 'data',
                'description': '1GB of data usage',
                'data_limit_gb': 1,
                'price': 100.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 4
            },
            {
                'name': '5GB Data',
                'ticket_type': 'data',
                'description': '5GB of data usage',
                'data_limit_gb': 5,
                'price': 400.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 5
            },
            {
                'name': '10GB Data',
                'ticket_type': 'data',
                'description': '10GB of data usage',
                'data_limit_gb': 10,
                'price': 700.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 6
            },
            {
                'name': 'Weekly Pass',
                'ticket_type': 'time',
                'description': '7 days of internet access',
                'duration_hours': 168,  # 7 days
                'price': 1000.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 7
            },
            {
                'name': 'Monthly Pass',
                'ticket_type': 'time',
                'description': '30 days of internet access',
                'duration_hours': 720,  # 30 days
                'price': 3000.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 8
            }
        ]

        created_count = 0
        for ticket_data in ticket_types:
            ticket_type, created = TicketType.objects.get_or_create(
                name=ticket_data['name'],
                defaults={
                    **ticket_data,
                    'created_by': admin_user
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created ticket type: {ticket_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Ticket type already exists: {ticket_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new ticket types')
        )

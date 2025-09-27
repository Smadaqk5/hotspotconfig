"""
Management command to create a Super Admin user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import SuperAdmin

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a Super Admin user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@hotspot.com', help='Super Admin email')
        parser.add_argument('--username', type=str, default='superadmin', help='Super Admin username')
        parser.add_argument('--password', type=str, default='admin123', help='Super Admin password')
        parser.add_argument('--first-name', type=str, default='Super', help='First name')
        parser.add_argument('--last-name', type=str, default='Admin', help='Last name')

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            return

        # Create Super Admin user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type='super_admin',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )

        # Create SuperAdmin profile
        SuperAdmin.objects.create(
            user=user,
            can_manage_providers=True,
            can_view_analytics=True,
            can_manage_system=True
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created Super Admin: {email}')
        )
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Login URL: http://127.0.0.1:8000/login/')

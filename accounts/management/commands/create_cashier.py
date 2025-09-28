from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import Provider, Cashier

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a cashier user for a provider'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email for the cashier'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Cashier123!',
            help='Password for the cashier (default: Cashier123!)'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the cashier (defaults to email prefix)'
        )
        parser.add_argument(
            '--provider-id',
            type=int,
            required=True,
            help='Provider ID to assign the cashier to'
        )
        parser.add_argument(
            '--employee-id',
            type=str,
            help='Employee ID for the cashier'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        username = options['username'] or email.split('@')[0]
        provider_id = options['provider_id']
        employee_id = options['employee_id']

        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Provider with ID {provider_id} not found.')
            )
            return

        with transaction.atomic():
            # Create or get user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': 'Cashier',
                    'last_name': 'User',
                    'user_type': 'cashier',
                    'is_verified': True,
                    'is_active': True,
                }
            )

            if not created:
                # Update existing user
                user.user_type = 'cashier'
                user.is_active = True
                user.save()

            # Set password
            user.set_password(password)
            user.save()

            # Create cashier profile
            cashier, cashier_created = Cashier.objects.get_or_create(
                user=user,
                defaults={
                    'provider': provider,
                    'employee_id': employee_id,
                    'can_generate_tickets': True,
                    'can_sell_tickets': True,
                    'can_view_sales': True,
                    'can_manage_users': False,
                    'can_download_configs': False,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Cashier user created successfully!\n'
                        f'   Email: {email}\n'
                        f'   Username: {username}\n'
                        f'   Password: {password}\n'
                        f'   Provider: {provider.business_name}\n'
                        f'   Employee ID: {employee_id or "Not set"}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Cashier user already exists and has been updated!\n'
                        f'   Email: {email}\n'
                        f'   Username: {username}\n'
                        f'   Password: {password}\n'
                        f'   Provider: {provider.business_name}\n'
                        f'   Employee ID: {employee_id or "Not set"}'
                    )
                )

            # Display login instructions
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🔐 Cashier Login Instructions:\n'
                    f'   1. Go to your Heroku app URL\n'
                    f'   2. Click "Login" or go to /login/\n'
                    f'   3. Use Email: {email}\n'
                    f'   4. Use Password: {password}\n'
                    f'   5. You will be redirected to the Cashier Dashboard!'
                )
            )

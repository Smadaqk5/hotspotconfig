from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import Provider

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a super admin user for the platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@hotspotplatform.com',
            help='Email for the super admin (default: admin@hotspotplatform.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='SuperAdmin123!',
            help='Password for the super admin (default: SuperAdmin123!)'
        )
        parser.add_argument(
            '--username',
            type=str,
            default='superadmin',
            help='Username for the super admin (default: superadmin)'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        username = options['username']

        with transaction.atomic():
            # Create or update super admin user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': 'Super',
                    'last_name': 'Admin',
                    'phone_number': '+254700000000',
                    'company_name': 'Hotspot Platform',
                    'is_verified': True,
                    'user_type': 'end_user',
                    'provider_license': 'SUPER-ADMIN-LICENSE',
                    'business_registration': 'SUPER-ADMIN-REG',
                    'location': 'Nairobi, Kenya',
                    'is_super_admin': True,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )

            if not created:
                # Update existing user to be super admin
                user.is_super_admin = True
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()

            # Set password
            user.set_password(password)
            user.save()

            # Create provider record for super admin
            provider, provider_created = Provider.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': 'Super Admin Provider',
                    'business_type': 'Platform Admin',
                    'contact_person': 'Super Admin',
                    'contact_phone': '+254700000000',
                    'contact_email': email,
                    'address': 'Nairobi, Kenya',
                    'city': 'Nairobi',
                    'county': 'Nairobi',
                    'country': 'Kenya',
                    'status': 'active',
                    'is_approved': True,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Super admin user created successfully!\n'
                        f'   Email: {email}\n'
                        f'   Username: {username}\n'
                        f'   Password: {password}\n'
                        f'   Provider ID: {provider.id if provider else "Not created"}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Super admin user already exists and has been updated!\n'
                        f'   Email: {email}\n'
                        f'   Username: {username}\n'
                        f'   Password: {password}\n'
                        f'   Provider ID: {provider.id if provider else "Not created"}'
                    )
                )

            # Display login instructions
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🔐 Login Instructions:\n'
                    f'   1. Go to your Heroku app URL\n'
                    f'   2. Click "Login" or go to /login/\n'
                    f'   3. Use Email: {email}\n'
                    f'   4. Use Password: {password}\n'
                    f'   5. You will have full super admin access!'
                )
            )

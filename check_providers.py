#!/usr/bin/env python
"""
Script to check providers and create a test cashier
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from accounts.models import Provider, User, Cashier

def check_providers():
    """Check available providers"""
    providers = Provider.objects.all()
    print('Available Providers:')
    for p in providers:
        print(f'ID: {p.id}, Name: {p.business_name}, Email: {p.contact_email}')
    
    if providers:
        # Create a test cashier for the first provider
        provider = providers[0]
        print(f'\nCreating test cashier for provider: {provider.business_name}')
        
        # Create test cashier user
        user, created = User.objects.get_or_create(
            email='cashier@test.com',
            defaults={
                'username': 'testcashier',
                'first_name': 'Test',
                'last_name': 'Cashier',
                'user_type': 'cashier',
                'is_verified': True,
                'is_active': True,
            }
        )
        
        if created:
            user.set_password('Cashier123!')
            user.save()
            print(f'✅ Created cashier user: {user.email}')
        else:
            print(f'⚠️  Cashier user already exists: {user.email}')
        
        # Create cashier profile
        cashier, cashier_created = Cashier.objects.get_or_create(
            user=user,
            defaults={
                'provider': provider,
                'employee_id': 'CASH001',
                'can_generate_tickets': True,
                'can_sell_tickets': True,
                'can_view_sales': True,
                'can_manage_users': False,
                'can_download_configs': False,
            }
        )
        
        if cashier_created:
            print(f'✅ Created cashier profile for provider: {provider.business_name}')
        else:
            print(f'⚠️  Cashier profile already exists')
        
        print(f'\n🔐 Test Cashier Login:')
        print(f'   Email: cashier@test.com')
        print(f'   Password: Cashier123!')
        print(f'   Provider: {provider.business_name}')
    else:
        print('No providers found. Please create a provider first.')

if __name__ == "__main__":
    check_providers()

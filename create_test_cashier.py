#!/usr/bin/env python
"""
Script to create a test cashier profile
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from accounts.models import Provider, User, Cashier

def create_test_cashier():
    """Create a test cashier profile"""
    try:
        # Get the first provider
        provider = Provider.objects.first()
        if not provider:
            print("❌ No providers found. Please create a provider first.")
            return
        
        print(f"✅ Found provider: {provider.business_name}")
        
        # Create cashier user
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
            print(f"✅ Created cashier user: {user.email}")
        else:
            print(f"⚠️  Cashier user already exists: {user.email}")
            # Update password in case it changed
            user.set_password('Cashier123!')
            user.save()
        
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
            print(f"✅ Created cashier profile for provider: {provider.business_name}")
        else:
            print(f"⚠️  Cashier profile already exists")
        
        print(f"\n🔐 Test Cashier Login Details:")
        print(f"   Email: cashier@test.com")
        print(f"   Password: Cashier123!")
        print(f"   Provider: {provider.business_name}")
        print(f"   Employee ID: CASH001")
        print(f"\n🎯 You can now login as a cashier to test the dashboard!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_cashier()

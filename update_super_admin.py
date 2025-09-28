#!/usr/bin/env python
"""
Script to update super admin user with additional fields
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Provider

User = get_user_model()

def update_super_admin():
    """Update super admin user with additional fields"""
    try:
        # Get the super admin user
        user = User.objects.get(email='adammainaj7@gmail.com')
        
        # Update additional fields
        user.is_super_admin = True
        user.phone_number = '+254700000000'
        user.company_name = 'Hotspot Platform'
        user.provider_license = 'SUPER-ADMIN-LICENSE'
        user.business_registration = 'SUPER-ADMIN-REG'
        user.location = 'Nairobi, Kenya'
        user.save()
        
        print(f"✅ Super admin updated: {user.email}")
        
        # Create provider record
        provider, created = Provider.objects.get_or_create(
            user=user,
            defaults={
                'business_name': 'Super Admin Provider',
                'business_type': 'Platform Admin',
                'contact_person': 'Super Admin',
                'contact_phone': '+254700000000',
                'contact_email': 'adammainaj7@gmail.com',
                'address': 'Nairobi, Kenya',
                'city': 'Nairobi',
                'county': 'Nairobi',
                'country': 'Kenya',
                'status': 'active',
                'is_approved': True,
            }
        )
        
        print(f"✅ Provider {'created' if created else 'already exists'}: {provider.id}")
        
        print(f"\n🔐 Super Admin Login Details:")
        print(f"   Email: adammainaj7@gmail.com")
        print(f"   Username: {user.username}")
        print(f"   Password: [as set during creation]")
        print(f"   Provider ID: {provider.id}")
        
    except User.DoesNotExist:
        print("❌ Super admin user not found. Please create one first.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_super_admin()

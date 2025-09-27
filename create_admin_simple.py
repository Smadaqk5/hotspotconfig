#!/usr/bin/env python
"""
Simple script to create a Super Admin user using Django's built-in User model
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

User = get_user_model()

def create_admin():
    print("🚀 Creating Super Admin user...")
    
    email = 'admin@hotspot.com'
    username = 'superadmin'
    password = 'admin123'
    first_name = 'Super'
    last_name = 'Admin'

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f"✅ User with email {email} already exists")
        print(f"📧 Email: {email}")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {password}")
        print(f"🌐 Login URL: http://127.0.0.1:8000/login/")
        print(f"🔧 Admin URL: http://127.0.0.1:8000/admin/")
        return

    try:
        # Create Super Admin user with basic fields only
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True
        )

        print('✅ Successfully created Super Admin!')
        print(f'📧 Email: {email}')
        print(f'👤 Username: {username}')
        print(f'🔑 Password: {password}')
        print(f'🌐 Login URL: http://127.0.0.1:8000/login/')
        print(f'🔧 Admin URL: http://127.0.0.1:8000/admin/')
        
    except Exception as e:
        print(f"❌ Error creating Super Admin: {e}")
        print("💡 The user might already exist or there's a database issue")
        
        # Try to find existing user
        try:
            user = User.objects.get(email=email)
            print(f"✅ Found existing user: {user.email}")
            print(f"🔑 You can reset password with: python manage.py changepassword {username}")
        except User.DoesNotExist:
            print("❌ No user found. Please check your database connection.")

if __name__ == '__main__':
    create_admin()

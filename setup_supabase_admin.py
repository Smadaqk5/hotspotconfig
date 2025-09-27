#!/usr/bin/env python
"""
Script to set up Supabase database and create Super Admin user
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
from django.db import connection

User = get_user_model()

def setup_supabase_admin():
    print("🚀 Setting up Supabase Super Admin...")
    
    # Check if we're using Supabase
    database_url = os.environ.get('DATABASE_URL', '')
    if 'supabase' in database_url.lower():
        print("✅ Supabase database detected!")
    else:
        print("⚠️  Using local SQLite database")
        print("To use Supabase, set your DATABASE_URL environment variable")
        print("Example: postgresql://postgres.abcdefghijklmnop:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    
    # Create Super Admin user
    email = 'admin@hotspot.com'
    username = 'superadmin'
    password = 'admin123'
    first_name = 'Super'
    last_name = 'Admin'

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f"✅ User with email {email} already exists")
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
        print("💡 Try running migrations first: python manage.py migrate")

if __name__ == '__main__':
    setup_supabase_admin()

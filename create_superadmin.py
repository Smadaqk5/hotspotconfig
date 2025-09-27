#!/usr/bin/env python
"""
Script to create a Super Admin user
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
from accounts.models import SuperAdmin

User = get_user_model()

def create_superadmin():
    email = 'admin@hotspot.com'
    username = 'superadmin'
    password = 'admin123'
    first_name = 'Super'
    last_name = 'Admin'

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f'User with email {email} already exists')
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

    print('Successfully created Super Admin!')
    print(f'Email: {email}')
    print(f'Username: {username}')
    print(f'Password: {password}')
    print(f'Login URL: http://127.0.0.1:8000/login/')

if __name__ == '__main__':
    create_superadmin()

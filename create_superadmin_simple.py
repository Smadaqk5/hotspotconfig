#!/usr/bin/env python
"""
Simple script to create a Super Admin user using Django shell
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

    print('Successfully created Super Admin!')
    print(f'Email: {email}')
    print(f'Username: {username}')
    print(f'Password: {password}')
    print(f'Login URL: http://127.0.0.1:8000/login/')

if __name__ == '__main__':
    create_superadmin()

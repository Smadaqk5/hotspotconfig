#!/usr/bin/env python
"""
Quick setup script for the MikroTik Hotspot Platform
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from django.core.management import execute_from_command_line

def quick_setup():
    print("🚀 Quick Setup for MikroTik Hotspot Platform")
    print("=" * 50)
    
    try:
        # Step 1: Create migrations
        print("📝 Step 1: Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
        print("✅ Migrations created")
        
        # Step 2: Apply migrations
        print("🔄 Step 2: Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations applied")
        
        # Step 3: Create Super Admin
        print("👤 Step 3: Creating Super Admin...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        email = 'admin@hotspot.com'
        username = 'superadmin'
        password = 'admin123'
        
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Super',
                last_name='Admin',
                is_staff=True,
                is_superuser=True
            )
            print("✅ Super Admin created")
        else:
            print("✅ Super Admin already exists")
        
        print("\n🎉 Setup Complete!")
        print("=" * 50)
        print(f"📧 Email: {email}")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {password}")
        print(f"🌐 Login URL: http://127.0.0.1:8000/login/")
        print(f"🔧 Admin URL: http://127.0.0.1:8000/admin/")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try running: python manage.py migrate")

if __name__ == '__main__':
    quick_setup()

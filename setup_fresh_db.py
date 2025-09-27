#!/usr/bin/env python
"""
Script to set up a fresh database with all migrations
"""
import os
import sys
import django
import subprocess

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

def setup_fresh_database():
    print("🚀 Setting up fresh database...")
    
    try:
        # Delete existing database if it exists
        if os.path.exists('db.sqlite3'):
            os.remove('db.sqlite3')
            print("✅ Deleted existing database")
        
        # Create fresh migrations
        print("📝 Creating fresh migrations...")
        result = subprocess.run([
            'python', 'manage.py', 'makemigrations', '--noinput'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error creating migrations: {result.stderr}")
            return False
        
        print("✅ Migrations created successfully")
        
        # Apply migrations
        print("🔄 Applying migrations...")
        result = subprocess.run([
            'python', 'manage.py', 'migrate', '--noinput'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error applying migrations: {result.stderr}")
            return False
        
        print("✅ Migrations applied successfully")
        
        # Create Super Admin user
        print("👤 Creating Super Admin user...")
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        email = 'admin@hotspot.com'
        username = 'superadmin'
        password = 'admin123'
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f"✅ User with email {email} already exists")
        else:
            # Create Super Admin user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Super',
                last_name='Admin',
                is_staff=True,
                is_superuser=True
            )
            print("✅ Super Admin user created successfully")
        
        print("\n🎉 Database setup complete!")
        print(f"📧 Email: {email}")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {password}")
        print(f"🌐 Login URL: http://127.0.0.1:8000/login/")
        print(f"🔧 Admin URL: http://127.0.0.1:8000/admin/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == '__main__':
    setup_fresh_database()

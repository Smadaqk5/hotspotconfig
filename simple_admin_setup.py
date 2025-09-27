#!/usr/bin/env python
"""
Simple script to create Super Admin without complex migrations
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

def create_simple_admin():
    print("🚀 Creating Super Admin user...")
    
    try:
        from django.contrib.auth import get_user_model
        from django.db import connection
        
        User = get_user_model()
        
        # Check if database exists
        if not os.path.exists('db.sqlite3'):
            print("📝 Creating fresh database...")
            # Create a simple database with just the User table
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS auth_user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        password VARCHAR(128) NOT NULL,
                        last_login DATETIME,
                        is_superuser BOOLEAN NOT NULL,
                        username VARCHAR(150) NOT NULL UNIQUE,
                        first_name VARCHAR(150) NOT NULL,
                        last_name VARCHAR(150) NOT NULL,
                        email VARCHAR(254) NOT NULL,
                        is_staff BOOLEAN NOT NULL,
                        is_active BOOLEAN NOT NULL,
                        date_joined DATETIME NOT NULL
                    )
                """)
        
        # Create Super Admin user
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
        print("💡 Try using Django's built-in createsuperuser command:")
        print("   python manage.py createsuperuser")

if __name__ == '__main__':
    create_simple_admin()

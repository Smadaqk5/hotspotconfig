#!/usr/bin/env python
"""
Complete setup script for MikroTik Hotspot Platform with Supabase
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

def complete_setup():
    print("🚀 Complete Setup for MikroTik Hotspot Platform")
    print("=" * 60)
    
    # Check if Supabase is configured
    database_url = os.environ.get('DATABASE_URL', '')
    if 'supabase' in database_url.lower():
        print("✅ Supabase database detected!")
        print(f"📊 Database: {database_url[:50]}...")
    else:
        print("⚠️  Using local SQLite database")
        print("💡 To use Supabase, set your DATABASE_URL environment variable")
        print("   Example: postgresql://postgres.abcdefghijklmnop:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    
    try:
        # Step 1: Apply basic migrations
        print("\n📝 Step 1: Applying basic migrations...")
        result = subprocess.run([
            'python', 'manage.py', 'migrate', 'auth', '--noinput'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error applying auth migrations: {result.stderr}")
            return False
        
        print("✅ Auth migrations applied")
        
        # Step 2: Apply contenttypes migrations
        print("\n📝 Step 2: Applying contenttypes migrations...")
        result = subprocess.run([
            'python', 'manage.py', 'migrate', 'contenttypes', '--noinput'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error applying contenttypes migrations: {result.stderr}")
            return False
        
        print("✅ Contenttypes migrations applied")
        
        # Step 3: Apply sessions migrations
        print("\n📝 Step 3: Applying sessions migrations...")
        result = subprocess.run([
            'python', 'manage.py', 'migrate', 'sessions', '--noinput'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Error applying sessions migrations: {result.stderr}")
            return False
        
        print("✅ Sessions migrations applied")
        
        # Step 4: Create Super Admin user
        print("\n👤 Step 4: Creating Super Admin user...")
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
        
        print("\n🎉 Setup Complete!")
        print("=" * 60)
        print(f"📧 Email: {email}")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {password}")
        print(f"🌐 Login URL: http://127.0.0.1:8000/login/")
        print(f"🔧 Admin URL: http://127.0.0.1:8000/admin/")
        print("=" * 60)
        print("\n💡 Next Steps:")
        print("1. Start the server: python manage.py runserver")
        print("2. Login with the credentials above")
        print("3. Apply remaining migrations: python manage.py migrate")
        print("4. Set up Supabase (optional): Follow SUPABASE_SETUP_GUIDE.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        print("💡 Try running individual commands:")
        print("   python manage.py migrate auth")
        print("   python manage.py migrate contenttypes")
        print("   python manage.py migrate sessions")
        return False

if __name__ == '__main__':
    complete_setup()

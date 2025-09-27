#!/usr/bin/env python
"""
GitHub Deployment Script for MikroTik Hotspot Platform
"""
import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def setup_environment():
    """Set up environment variables for GitHub deployment"""
    # Set production environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
    os.environ.setdefault('DEBUG', 'False')
    os.environ.setdefault('ALLOWED_HOSTS', '*')
    
    # Set a secure secret key for production
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'django-insecure-change-this-in-production-please-use-a-secure-key'
    
    # Database configuration
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
    
    # Email configuration (use console backend for GitHub)
    os.environ.setdefault('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
    
    print("✅ Environment variables configured for GitHub deployment")

def run_migrations():
    """Run database migrations"""
    try:
        print("🔄 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    return True

def collect_static():
    """Collect static files"""
    try:
        print("🔄 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected")
    except Exception as e:
        print(f"❌ Static files error: {e}")
        return False
    return True

def create_superuser():
    """Create a superuser if none exists"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            print("🔄 Creating superuser...")
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                user_type='super_admin'
            )
            print("✅ Superuser created (username: admin, password: admin123)")
        else:
            print("✅ Superuser already exists")
    except Exception as e:
        print(f"❌ Superuser creation error: {e}")
        return False
    return True

def main():
    """Main deployment function"""
    print("🚀 Starting GitHub deployment...")
    
    # Setup environment
    setup_environment()
    
    # Initialize Django
    django.setup()
    
    # Run deployment steps
    if not run_migrations():
        sys.exit(1)
    
    if not collect_static():
        sys.exit(1)
    
    if not create_superuser():
        sys.exit(1)
    
    print("🎉 GitHub deployment completed successfully!")
    print("📝 Access the application and login with:")
    print("   Username: admin")
    print("   Password: admin123")

if __name__ == '__main__':
    main()

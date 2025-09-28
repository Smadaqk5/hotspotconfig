#!/usr/bin/env python3
"""
Script to set Heroku environment variables
Run this script to automatically configure your Heroku app
"""

import subprocess
import sys

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def set_heroku_env_vars():
    """Set all required environment variables on Heroku"""
    
    # Environment variables to set
    env_vars = {
        # Django Settings
        'SECRET_KEY': 'stIxCFY89xrhHr3T5lguRB1W1SnSTCy0zDxHXC1gr0o2nI95znL6PrDJywTmuRblpSU',
        'DEBUG': 'False',
        'ALLOWED_HOSTS': 'hotspott-39e105144510.herokuapp.com',
        
        # Database (Supabase PostgreSQL)
        'DATABASE_URL': 'postgresql://postgres.vbrkdpjaplqrngarnhyu:C7kCNrGZa$E8S7W@aws-1-eu-north-1.pooler.supabase.com:6543/postgres',
        'SUPABASE_URL': 'https://vbrkdpjaplqrngarnhyu.supabase.co',
        'SUPABASE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZicmtkcGphcGxxcm5nYXJnaHl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5NTM1NjUsImV4cCI6MjA3NDUyOTU2NX0.6GD8quMGFMl6TCgTnFj8UijcBgXQpaO8cISUfiW61Iw',
        'SUPABASE_SERVICE_ROLE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZicmtkcGphcGxxcm5nYXJnaHl1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODk1MzU2NSwiZXhwIjoyMDc0NTI5NTY1fQ.EcuFAtDtYoafFznel4ZSuIeP3BYC6HyT3z_sCEnrHRg',
        
        # Encryption Key (IMPORTANT: Generate a new one for production)
        'ENCRYPTION_KEY': 'your-fernet-encryption-key-here',
        
        # Pesapal API (Platform Revenue)
        'PESAPAL_CONSUMER_KEY': 'c7tKYh47BTA3kqExs7OOI8ghj2emni62',
        'PESAPAL_CONSUMER_SECRET': 'jQcz5iYPZW121PW2kUU+o3piBO4=',
        'PESAPAL_BASE_URL': 'https://cybqa.pesapal.com/pesapalv3/api/',
        'PESAPAL_CALLBACK_URL': 'https://hotspott-39e105144510.herokuapp.com/api/payments/pesapal/callback/',
        'PESAPAL_IPN_URL': 'https://hotspott-39e105144510.herokuapp.com/api/payments/pesapal/ipn/',
        
        # Email Settings
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': '587',
        'EMAIL_USE_TLS': 'True',
        'EMAIL_HOST_USER': 'mainaadam277@gmail.com',
        'EMAIL_HOST_PASSWORD': 'cwch eysq lofx tubi',
        'DEFAULT_FROM_EMAIL': 'mainaadam277@gmail.com',
        
        # Frontend URL
        'FRONTEND_URL': 'https://hotspott-39e105144510.herokuapp.com/',
        
        # Additional Required Variables
        'DJANGO_SETTINGS_MODULE': 'hotspot_config.settings',
        'PYTHONPATH': '/app'
    }
    
    print("🚀 Setting Heroku environment variables...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(env_vars)
    
    for key, value in env_vars.items():
        print(f"Setting {key}...")
        
        # Escape the value for shell command
        escaped_value = value.replace('"', '\\"').replace('$', '\\$')
        command = f'heroku config:set {key}="{escaped_value}"'
        
        success, stdout, stderr = run_command(command)
        
        if success:
            print(f"✅ {key} set successfully")
            success_count += 1
        else:
            print(f"❌ Failed to set {key}: {stderr}")
    
    print("=" * 50)
    print(f"📊 Results: {success_count}/{total_count} variables set successfully")
    
    if success_count == total_count:
        print("🎉 All environment variables set successfully!")
        print("\n📋 Next steps:")
        print("1. Run: heroku run python manage.py migrate")
        print("2. Run: heroku run python manage.py createsuperuser")
        print("3. Run: heroku run python manage.py collectstatic --noinput")
        print("4. Visit: https://hotspott-39e105144510.herokuapp.com/")
    else:
        print("⚠️  Some variables failed to set. Please check the errors above.")
    
    return success_count == total_count

if __name__ == "__main__":
    print("🔧 Heroku Environment Variables Setup")
    print("=" * 50)
    
    # Check if Heroku CLI is installed
    success, stdout, stderr = run_command("heroku --version")
    if not success:
        print("❌ Heroku CLI not found. Please install it first:")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        sys.exit(1)
    
    # Check if logged in to Heroku
    success, stdout, stderr = run_command("heroku auth:whoami")
    if not success:
        print("❌ Not logged in to Heroku. Please run:")
        print("   heroku login")
        sys.exit(1)
    
    # Set environment variables
    if set_heroku_env_vars():
        print("\n🎉 Setup complete! Your app is ready for deployment.")
    else:
        print("\n⚠️  Setup completed with some errors. Please review the output above.")

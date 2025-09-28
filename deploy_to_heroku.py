#!/usr/bin/env python3
"""
Complete Heroku deployment script for MikroTik Hotspot Platform
"""

import subprocess
import sys
import time

def run_command(command, description=""):
    """Run a command and return the result"""
    print(f"🔄 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def deploy_to_heroku():
    """Complete deployment process"""
    
    print("🚀 MikroTik Hotspot Platform - Heroku Deployment")
    print("=" * 60)
    
    # Step 1: Check Heroku CLI
    print("\n📋 Step 1: Checking Heroku CLI...")
    if not run_command("heroku --version", "Check Heroku CLI"):
        print("❌ Heroku CLI not found. Please install it first:")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Step 2: Check login status
    print("\n📋 Step 2: Checking Heroku login...")
    if not run_command("heroku auth:whoami", "Check Heroku login"):
        print("❌ Not logged in to Heroku. Please run:")
        print("   heroku login")
        return False
    
    # Step 3: Set environment variables
    print("\n📋 Step 3: Setting environment variables...")
    env_vars = [
        ('SECRET_KEY', 'stIxCFY89xrhHr3T5lguRB1W1SnSTCy0zDxHXC1gr0o2nI95znL6PrDJywTmuRblpSU'),
        ('DEBUG', 'False'),
        ('ALLOWED_HOSTS', 'hotspott-39e105144510.herokuapp.com'),
        ('DATABASE_URL', 'postgresql://postgres.vbrkdpjaplqrngarnhyu:C7kCNrGZa$E8S7W@aws-1-eu-north-1.pooler.supabase.com:6543/postgres'),
        ('SUPABASE_URL', 'https://vbrkdpjaplqrngarnhyu.supabase.co'),
        ('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZicmtkcGphcGxxcm5nYXJnaHl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5NTM1NjUsImV4cCI6MjA3NDUyOTU2NX0.6GD8quMGFMl6TCgTnFj8UijcBgXQpaO8cISUfiW61Iw'),
        ('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZicmtkcGphcGxxcm5nYXJnaHl1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODk1MzU2NSwiZXhwIjoyMDc0NTI5NTY1fQ.EcuFAtDtYoafFznel4ZSuIeP3BYC6HyT3z_sCEnrHRg'),
        ('ENCRYPTION_KEY', 'your-fernet-encryption-key-here'),
        ('PESAPAL_CONSUMER_KEY', 'c7tKYh47BTA3kqExs7OOI8ghj2emni62'),
        ('PESAPAL_CONSUMER_SECRET', 'jQcz5iYPZW121PW2kUU+o3piBO4='),
        ('PESAPAL_BASE_URL', 'https://cybqa.pesapal.com/pesapalv3/api/'),
        ('PESAPAL_CALLBACK_URL', 'https://hotspott-39e105144510.herokuapp.com/api/payments/pesapal/callback/'),
        ('PESAPAL_IPN_URL', 'https://hotspott-39e105144510.herokuapp.com/api/payments/pesapal/ipn/'),
        ('EMAIL_HOST', 'smtp.gmail.com'),
        ('EMAIL_PORT', '587'),
        ('EMAIL_USE_TLS', 'True'),
        ('EMAIL_HOST_USER', 'mainaadam277@gmail.com'),
        ('EMAIL_HOST_PASSWORD', 'cwch eysq lofx tubi'),
        ('DEFAULT_FROM_EMAIL', 'mainaadam277@gmail.com'),
        ('FRONTEND_URL', 'https://hotspott-39e105144510.herokuapp.com/'),
        ('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings'),
        ('PYTHONPATH', '/app')
    ]
    
    for key, value in env_vars:
        escaped_value = value.replace('"', '\\"').replace('$', '\\$')
        command = f'heroku config:set {key}="{escaped_value}"'
        if not run_command(command, f"Set {key}"):
            print(f"⚠️  Failed to set {key}, continuing...")
    
    # Step 4: Deploy to Heroku
    print("\n📋 Step 4: Deploying to Heroku...")
    if not run_command("git push heroku main", "Deploy to Heroku"):
        print("❌ Deployment failed. Please check the errors above.")
        return False
    
    # Step 5: Run migrations
    print("\n📋 Step 5: Running database migrations...")
    if not run_command("heroku run python manage.py migrate", "Run migrations"):
        print("⚠️  Migrations failed, but continuing...")
    
    # Step 6: Collect static files
    print("\n📋 Step 6: Collecting static files...")
    if not run_command("heroku run python manage.py collectstatic --noinput", "Collect static files"):
        print("⚠️  Static files collection failed, but continuing...")
    
    # Step 7: Create superuser (optional)
    print("\n📋 Step 7: Creating superuser...")
    print("   You can create a superuser manually with:")
    print("   heroku run python manage.py createsuperuser")
    
    # Step 8: Open the app
    print("\n📋 Step 8: Opening the app...")
    if run_command("heroku open", "Open the app"):
        print("🎉 Deployment successful!")
        print("\n📋 Your app is now live at:")
        print("   https://hotspott-39e105144510.herokuapp.com/")
        
        print("\n📋 Next steps:")
        print("1. Create a superuser: heroku run python manage.py createsuperuser")
        print("2. Test the payment flows in sandbox mode")
        print("3. Configure your first provider's M-PESA credentials")
        print("4. Set up Heroku Scheduler for automation tasks")
        
        return True
    else:
        print("❌ Failed to open the app, but deployment may have succeeded.")
        return False

if __name__ == "__main__":
    print("🔧 MikroTik Hotspot Platform - Heroku Deployment")
    print("=" * 60)
    
    # Check if we're in a git repository
    if not run_command("git status", "Check git repository"):
        print("❌ Not in a git repository. Please run this from your project directory.")
        sys.exit(1)
    
    # Check if Heroku remote exists
    if not run_command("git remote -v | grep heroku", "Check Heroku remote"):
        print("❌ Heroku remote not found. Please add it first:")
        print("   heroku git:remote -a hotspott-39e105144510")
        sys.exit(1)
    
    # Start deployment
    if deploy_to_heroku():
        print("\n🎉 Deployment completed successfully!")
        print("Your MikroTik Hotspot Platform is now live!")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")
        sys.exit(1)

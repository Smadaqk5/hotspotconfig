"""
Temporary settings to use Django's default User model
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django with default User model
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

def create_admin_with_default_user():
    print("🚀 Creating Super Admin with default User model...")
    
    try:
        from django.contrib.auth.models import User
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    create_admin_with_default_user()

#!/usr/bin/env python3
"""
Script to fix Django migration issues
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def fix_migration_state():
    """Fix Django migration state"""
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
    django.setup()
    
    print("🔧 Fixing Django migration state...")
    
    try:
        # Mark all migrations as applied without running them
        print("1️⃣ Marking migrations as applied...")
        execute_from_command_line(['manage.py', 'migrate', '--fake'])
        
        print("2️⃣ Running collectstatic...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        print("3️⃣ Creating superuser...")
        execute_from_command_line(['manage.py', 'createsuperuser', '--email', 'admin@example.com', '--noinput'])
        
        print("✅ Migration fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing migrations: {e}")
        return False

def reset_database():
    """Reset database completely"""
    print("⚠️  This will delete all data in your database!")
    confirm = input("Are you sure you want to reset? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Database reset cancelled.")
        return False
    
    try:
        print("🔄 Resetting database...")
        execute_from_command_line(['manage.py', 'flush', '--noinput'])
        
        print("🔄 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("🔄 Creating superuser...")
        execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
        
        print("✅ Database reset completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Django Migration Fix Tool")
    print("=" * 50)
    
    print("\nChoose an option:")
    print("1. Fix migration state (keep existing data)")
    print("2. Reset database completely (delete all data)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        fix_migration_state()
    elif choice == "2":
        reset_database()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Exiting.")

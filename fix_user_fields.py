#!/usr/bin/env python
"""
Script to manually add all missing User model fields to the database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from django.db import connection

def fix_user_fields():
    """Add all missing fields to accounts_user table"""
    with connection.cursor() as cursor:
        print("🔧 Checking and fixing User model fields...")
        
        # Check if we're using SQLite or PostgreSQL
        try:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='accounts_user'")
            is_sqlite = bool(cursor.fetchone())
        except:
            is_sqlite = False
        
        if is_sqlite:
            print("📱 Using SQLite database")
            # SQLite: Check existing columns
            cursor.execute("PRAGMA table_info(accounts_user)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"📋 Existing columns: {columns}")
            
            # Add missing fields
            fields_to_add = [
                ('user_type', "VARCHAR(20) DEFAULT 'end_user'"),
                ('provider_license', 'VARCHAR(100)'),
                ('business_registration', 'VARCHAR(100)'),
                ('location', 'VARCHAR(200)'),
                ('is_super_admin', 'BOOLEAN DEFAULT 0'),
                ('created_at', 'DATETIME'),
                ('updated_at', 'DATETIME'),
            ]
        else:
            print("🐘 Using PostgreSQL database")
            # PostgreSQL: Check existing columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'accounts_user'
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print(f"📋 Existing columns: {columns}")
            
            # Add missing fields
            fields_to_add = [
                ('user_type', "VARCHAR(20) DEFAULT 'end_user'"),
                ('provider_license', 'VARCHAR(100)'),
                ('business_registration', 'VARCHAR(100)'),
                ('location', 'VARCHAR(200)'),
                ('is_super_admin', 'BOOLEAN DEFAULT FALSE'),
                ('created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
                ('updated_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
            ]
        
        # Add missing fields
        added_count = 0
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE accounts_user ADD COLUMN {field_name} {field_type}")
                    print(f"✅ Added {field_name} field")
                    added_count += 1
                except Exception as e:
                    print(f"❌ Failed to add {field_name}: {e}")
            else:
                print(f"ℹ️  {field_name} field already exists")
        
        print(f"\n🎉 Migration complete! Added {added_count} new fields.")
        print("✅ User model fields are now properly configured!")

if __name__ == "__main__":
    fix_user_fields()
Script to manually add all missing user fields to accounts_user table
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from django.db import connection

def add_all_missing_fields():
    """Add all missing fields to accounts_user table"""
    with connection.cursor() as cursor:
        # Check if we're using SQLite or PostgreSQL
        try:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='accounts_user'")
            is_sqlite = cursor.fetchone() is not None
        except:
            is_sqlite = False
        
        if is_sqlite:
            print("Detected SQLite database")
            # SQLite: Use PRAGMA to check columns
            cursor.execute("PRAGMA table_info(accounts_user)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Add missing fields
            fields_to_add = [
                ('provider_license', 'VARCHAR(100)'),
                ('business_registration', 'VARCHAR(100)'),
                ('location', 'VARCHAR(200)'),
                ('is_super_admin', 'BOOLEAN DEFAULT 0'),
                ('created_at', 'DATETIME'),
                ('updated_at', 'DATETIME'),
            ]
            
        else:
            print("Detected PostgreSQL database")
            # PostgreSQL: Use information_schema
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'accounts_user'
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            # Add missing fields
            fields_to_add = [
                ('provider_license', 'VARCHAR(100)'),
                ('business_registration', 'VARCHAR(100)'),
                ('location', 'VARCHAR(200)'),
                ('is_super_admin', 'BOOLEAN DEFAULT FALSE'),
                ('created_at', 'TIMESTAMP WITH TIME ZONE'),
                ('updated_at', 'TIMESTAMP WITH TIME ZONE'),
            ]
        
        print(f"Existing columns: {columns}")
        
        # Add missing fields
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                print(f"Adding {field_name} field...")
                cursor.execute(f"ALTER TABLE accounts_user ADD COLUMN {field_name} {field_type}")
                print(f"✅ {field_name} field added successfully!")
            else:
                print(f"✅ {field_name} field already exists!")

if __name__ == "__main__":
    add_all_missing_fields()
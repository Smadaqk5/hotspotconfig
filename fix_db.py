#!/usr/bin/env python
"""
Simple script to fix database schema on Heroku
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from django.db import connection

def fix_database():
    """Fix the database schema by adding missing columns"""
    with connection.cursor() as cursor:
        print("🔧 Fixing database schema...")
        
        # Check existing columns
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
        
        added_count = 0
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE accounts_user ADD COLUMN {field_name} {field_type}")
                    print(f"✅ Added {field_name}")
                    added_count += 1
                except Exception as e:
                    print(f"❌ Failed to add {field_name}: {e}")
            else:
                print(f"ℹ️  {field_name} already exists")
        
        print(f"\n🎉 Added {added_count} new fields!")
        print("✅ Database schema is now fixed!")

if __name__ == "__main__":
    fix_database()

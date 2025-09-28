#!/usr/bin/env python3
"""
Fix missing user_type column in accounts_user table
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from django.db import connection

def fix_user_type_column():
    """Add the missing user_type column to accounts_user table"""
    try:
        with connection.cursor() as cursor:
            # Check if column exists
            cursor.execute("""
                SELECT COUNT(*) FROM pragma_table_info('accounts_user') 
                WHERE name = 'user_type'
            """)
            column_exists = cursor.fetchone()[0] > 0
            
            if not column_exists:
                print("Adding user_type column to accounts_user table...")
                
                # Add the user_type column
                cursor.execute("""
                    ALTER TABLE accounts_user 
                    ADD COLUMN user_type VARCHAR(20) DEFAULT 'end_user'
                """)
                
                print("✅ user_type column added successfully!")
            else:
                print("✅ user_type column already exists!")
                
            # Verify the column was added
            cursor.execute("""
                SELECT COUNT(*) FROM pragma_table_info('accounts_user') 
                WHERE name = 'user_type'
            """)
            column_exists = cursor.fetchone()[0] > 0
            
            if column_exists:
                print("✅ Verification: user_type column is now present!")
                return True
            else:
                print("❌ Verification failed: user_type column still missing!")
                return False
                
    except Exception as e:
        print(f"❌ Error fixing user_type column: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing missing user_type column...")
    if fix_user_type_column():
        print("🎉 user_type column fixed successfully!")
    else:
        print("❌ Failed to fix user_type column!")

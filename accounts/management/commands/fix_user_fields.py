from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix missing User model fields in database'

    def handle(self, *args, **options):
        """Add all missing fields to accounts_user table"""
        with connection.cursor() as cursor:
            self.stdout.write("🔧 Checking and fixing User model fields...")
            
            # Check if we're using SQLite or PostgreSQL
            try:
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='accounts_user'")
                is_sqlite = bool(cursor.fetchone())
            except:
                is_sqlite = False
            
            if is_sqlite:
                self.stdout.write("📱 Using SQLite database")
                # SQLite: Check existing columns
                cursor.execute("PRAGMA table_info(accounts_user)")
                columns = [row[1] for row in cursor.fetchall()]
                self.stdout.write(f"📋 Existing columns: {columns}")
                
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
                self.stdout.write("🐘 Using PostgreSQL database")
                # PostgreSQL: Check existing columns
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'accounts_user'
                """)
                columns = [row[0] for row in cursor.fetchall()]
                self.stdout.write(f"📋 Existing columns: {columns}")
                
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
                        self.stdout.write(f"✅ Added {field_name} field")
                        added_count += 1
                    except Exception as e:
                        self.stdout.write(f"❌ Failed to add {field_name}: {e}")
                else:
                    self.stdout.write(f"ℹ️  {field_name} field already exists")
            
            self.stdout.write(f"\n🎉 Migration complete! Added {added_count} new fields.")
            self.stdout.write("✅ User model fields are now properly configured!")
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Add all missing user fields to accounts_user table'

    def handle(self, *args, **options):
        """Add all missing fields to accounts_user table"""
        with connection.cursor() as cursor:
            # Check if we're using SQLite or PostgreSQL
            try:
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='accounts_user'")
                is_sqlite = cursor.fetchone() is not None
            except:
                is_sqlite = False
            
            if is_sqlite:
                self.stdout.write("Detected SQLite database")
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
                self.stdout.write("Detected PostgreSQL database")
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
            
            self.stdout.write(f"Existing columns: {columns}")
            
            # Add missing fields
            for field_name, field_type in fields_to_add:
                if field_name not in columns:
                    self.stdout.write(f"Adding {field_name} field...")
                    cursor.execute(f"ALTER TABLE accounts_user ADD COLUMN {field_name} {field_type}")
                    self.stdout.write(self.style.SUCCESS(f"✅ {field_name} field added successfully!"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"✅ {field_name} field already exists!"))
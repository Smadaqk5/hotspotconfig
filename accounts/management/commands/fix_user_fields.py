from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Add missing user fields to accounts_user table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if columns exist (PostgreSQL syntax)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'accounts_user'
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write(f"Existing columns: {columns}")
            
            # Add missing fields
            fields_to_add = [
                ('provider_license', 'VARCHAR(100)'),
                ('business_registration', 'VARCHAR(100)'),
                ('location', 'VARCHAR(200)'),
                ('is_super_admin', 'BOOLEAN DEFAULT FALSE'),
                ('created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'),
                ('updated_at', 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()')
            ]
            
            for field_name, field_type in fields_to_add:
                if field_name not in columns:
                    self.stdout.write(f"Adding {field_name}...")
                    cursor.execute(f"ALTER TABLE accounts_user ADD COLUMN {field_name} {field_type}")
                    self.stdout.write(self.style.SUCCESS(f"✅ {field_name} added successfully!"))
                else:
                    self.stdout.write(f"✅ {field_name} already exists!")

# Generated manually to add all missing user fields

from django.db import migrations, models


def add_all_missing_fields(apps, schema_editor):
    """Add all missing fields to accounts_user table"""
    with schema_editor.connection.cursor() as cursor:
        # Check if we're using SQLite or PostgreSQL
        try:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='accounts_user'")
            is_sqlite = True
        except:
            is_sqlite = False
        
        if is_sqlite:
            # SQLite: Use PRAGMA to check columns
            cursor.execute("PRAGMA table_info(accounts_user)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Add missing fields
            if 'provider_license' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN provider_license VARCHAR(100)")
            
            if 'business_registration' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN business_registration VARCHAR(100)")
            
            if 'location' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN location VARCHAR(200)")
            
            if 'is_super_admin' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN is_super_admin BOOLEAN DEFAULT 0")
            
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN created_at DATETIME")
            
            if 'updated_at' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN updated_at DATETIME")
                
        else:
            # PostgreSQL: Use information_schema
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'accounts_user'
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            # Add missing fields
            if 'provider_license' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN provider_license VARCHAR(100)")
            
            if 'business_registration' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN business_registration VARCHAR(100)")
            
            if 'location' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN location VARCHAR(200)")
            
            if 'is_super_admin' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN is_super_admin BOOLEAN DEFAULT FALSE")
            
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN created_at TIMESTAMP WITH TIME ZONE")
            
            if 'updated_at' not in columns:
                cursor.execute("ALTER TABLE accounts_user ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE")


def reverse_add_all_missing_fields(apps, schema_editor):
    """Reverse operation - do nothing to avoid data loss"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_add_user_type_field'),
    ]

    operations = [
        migrations.RunPython(
            add_all_missing_fields,
            reverse_add_all_missing_fields,
        ),
    ]
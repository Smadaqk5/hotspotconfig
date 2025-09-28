# Generated manually for PostgreSQL - add missing user fields

from django.db import migrations, models


def add_postgresql_user_fields(apps, schema_editor):
    """Add all missing fields to accounts_user table (PostgreSQL only)"""
    with schema_editor.connection.cursor() as cursor:
        # Get existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'accounts_user'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
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
        
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                cursor.execute(f"ALTER TABLE accounts_user ADD COLUMN {field_name} {field_type}")


def reverse_add_postgresql_user_fields(apps, schema_editor):
    """Reverse operation - do nothing"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_add_all_missing_user_fields'),
    ]

    operations = [
        migrations.RunPython(
            add_postgresql_user_fields,
            reverse_add_postgresql_user_fields,
        ),
    ]

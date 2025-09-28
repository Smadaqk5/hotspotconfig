# Generated manually to fix User fields on PostgreSQL (Heroku)

from django.db import migrations, models


def add_missing_user_fields_postgresql(apps, schema_editor):
    """Add all missing fields to accounts_user table for PostgreSQL"""
    with schema_editor.connection.cursor() as cursor:
        # PostgreSQL: Use information_schema to check existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'accounts_user'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        print(f"Existing columns: {columns}")
        
        # Add missing fields for PostgreSQL
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
                try:
                    cursor.execute(f"ALTER TABLE accounts_user ADD COLUMN {field_name} {field_type}")
                    print(f"✅ Added {field_name} field")
                except Exception as e:
                    print(f"❌ Failed to add {field_name}: {e}")
            else:
                print(f"ℹ️  {field_name} field already exists")


def reverse_add_missing_user_fields_postgresql(apps, schema_editor):
    """Reverse operation - do nothing"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_add_all_missing_user_fields'),
    ]

    operations = [
        migrations.RunPython(
            add_missing_user_fields_postgresql,
            reverse_add_missing_user_fields_postgresql,
        ),
    ]

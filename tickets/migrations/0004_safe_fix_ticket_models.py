# Generated manually to safely fix ticket model issues

from django.db import migrations, models
import django.db.models.deletion


def safe_add_fields(apps, schema_editor):
    """Safely add fields only if they don't exist"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Check if columns exist and add them if they don't
        # Use SQLite syntax for checking column existence
        cursor.execute("PRAGMA table_info(tickets_ticket)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'plan_type' not in columns:
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN plan_type VARCHAR(10) DEFAULT 'time'")
        
        if 'duration_hours' not in columns:
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN duration_hours INTEGER")
        
        if 'data_limit_mb' not in columns:
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN data_limit_mb INTEGER")
        
        if 'data_used_mb' not in columns:
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN data_used_mb INTEGER DEFAULT 0")
        
        if 'price' not in columns:
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN price DECIMAL(10,2) DEFAULT 0")
        
        if 'currency' not in columns:
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN currency VARCHAR(3) DEFAULT 'KES'")


def reverse_safe_add_fields(apps, schema_editor):
    """Reverse operation - do nothing"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_alter_tickettype_options_alter_ticketusage_options_and_more'),
    ]

    operations = [
        migrations.RunPython(
            safe_add_fields,
            reverse_safe_add_fields,
        ),
    ]

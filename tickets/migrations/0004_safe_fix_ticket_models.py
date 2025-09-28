# Generated manually to safely fix ticket model issues

from django.db import migrations, models
import django.db.models.deletion


def safe_add_fields(apps, schema_editor):
    """Safely add fields only if they don't exist"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Check if columns exist and add them if they don't
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'tickets_ticket' AND column_name = 'plan_type'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN plan_type VARCHAR(10) DEFAULT 'time'")
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'tickets_ticket' AND column_name = 'duration_hours'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN duration_hours INTEGER")
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'tickets_ticket' AND column_name = 'data_limit_mb'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN data_limit_mb INTEGER")
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'tickets_ticket' AND column_name = 'data_used_mb'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN data_used_mb INTEGER DEFAULT 0")
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'tickets_ticket' AND column_name = 'price'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE tickets_ticket ADD COLUMN price DECIMAL(10,2) DEFAULT 0")
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'tickets_ticket' AND column_name = 'currency'
        """)
        if not cursor.fetchone():
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

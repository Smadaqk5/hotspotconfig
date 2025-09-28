# Generated manually to add missing user_type field

from django.db import migrations, models


def add_user_type_field(apps, schema_editor):
    """Add user_type field if it doesn't exist"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Check if column exists
        cursor.execute("""
            SELECT COUNT(*) FROM pragma_table_info('accounts_user') 
            WHERE name = 'user_type'
        """)
        column_exists = cursor.fetchone()[0] > 0
        
        if not column_exists:
            # Add the column
            cursor.execute("""
                ALTER TABLE accounts_user 
                ADD COLUMN user_type VARCHAR(20) DEFAULT 'end_user'
            """)


def reverse_add_user_type_field(apps, schema_editor):
    """Remove user_type field"""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("ALTER TABLE accounts_user DROP COLUMN user_type")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_user_user_type'),
    ]

    operations = [
        migrations.RunPython(
            add_user_type_field,
            reverse_add_user_type_field,
        ),
    ]

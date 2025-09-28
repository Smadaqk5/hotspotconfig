# Generated manually to add missing user_type field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_user_user_type'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS user_type VARCHAR(20) DEFAULT 'end_user';",
            reverse_sql="ALTER TABLE accounts_user DROP COLUMN IF EXISTS user_type;"
        ),
    ]

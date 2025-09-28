# Generated manually to fix ticket model issues

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_alter_tickettype_options_alter_ticketusage_options_and_more'),
    ]

    operations = [
        # Add missing fields to Ticket model
        migrations.AddField(
            model_name='ticket',
            name='plan_type',
            field=models.CharField(default='time', max_length=10),
        ),
        migrations.AddField(
            model_name='ticket',
            name='duration_hours',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='data_limit_mb',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='data_used_mb',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ticket',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, default=0),
        ),
        migrations.AddField(
            model_name='ticket',
            name='currency',
            field=models.CharField(default='KES', max_length=3),
        ),
        migrations.AddField(
            model_name='ticket',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.payment'),
        ),
        
        # Add missing fields to TicketType model
        migrations.AddField(
            model_name='tickettype',
            name='type',
            field=models.CharField(default='time', max_length=10),
        ),
        migrations.AddField(
            model_name='tickettype',
            name='duration_hours',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tickettype',
            name='data_limit_mb',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tickettype',
            name='download_speed_mbps',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='tickettype',
            name='upload_speed_mbps',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='tickettype',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tickettype',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tickettype',
            name='icon',
            field=models.CharField(default='fas fa-wifi', max_length=50),
        ),
        migrations.AddField(
            model_name='tickettype',
            name='color',
            field=models.CharField(default='#3B82F6', max_length=7),
        ),
        
        # Add missing fields to TicketSale model
        migrations.AddField(
            model_name='ticketsale',
            name='ticket_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.tickettype'),
        ),
        migrations.AddField(
            model_name='ticketsale',
            name='ticket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tickets.ticket'),
        ),
        migrations.AddField(
            model_name='ticketsale',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='ticketsale',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]

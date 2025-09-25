"""
Signals for tickets app
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Ticket, TicketSale


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, created, **kwargs):
    """Handle ticket post-save events"""
    if created:
        # Set expiry date for time-based tickets
        if (instance.ticket_type.ticket_type == 'time' and 
            instance.ticket_type.duration_hours and 
            not instance.expires_at):
            instance.expires_at = timezone.now() + timezone.timedelta(
                hours=instance.ticket_type.duration_hours
            )
            instance.save(update_fields=['expires_at'])


@receiver(post_save, sender=TicketSale)
def ticket_sale_post_save(sender, instance, created, **kwargs):
    """Handle ticket sale post-save events"""
    if created:
        # Update ticket status when sold
        if instance.ticket.status == 'active':
            instance.ticket.status = 'used'
            instance.ticket.activated_at = timezone.now()
            instance.ticket.save(update_fields=['status', 'activated_at'])


@receiver(pre_save, sender=Ticket)
def ticket_pre_save(sender, instance, **kwargs):
    """Handle ticket pre-save events"""
    # Check if ticket is expired
    if instance.expires_at and timezone.now() > instance.expires_at:
        if instance.status == 'active':
            instance.status = 'expired'
    
    # Generate username and password if not provided
    if not instance.username:
        instance.username = instance.generate_username()
    
    if not instance.password:
        instance.password = instance.generate_password()

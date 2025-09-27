from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid
import secrets
import string

User = get_user_model()


class TicketType(models.Model):
    """Ticket types (time-based or data-based)"""
    TYPE_CHOICES = [
        ('time', 'Time-based'),
        ('data', 'Data-based'),
    ]
    
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='ticket_types', null=True, blank=True)
    name = models.CharField(max_length=100, default='Default Ticket')
    ticket_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='time')
    value = models.IntegerField(help_text="Time in hours or data in GB", default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['provider', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.provider.business_name}"


class Ticket(models.Model):
    """Individual tickets/vouchers"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='tickets')
    code = models.CharField(max_length=20, unique=True, default='TEMP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Ticket details
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    
    # Usage tracking
    time_used = models.IntegerField(default=0, help_text="Time used in minutes")
    data_used = models.IntegerField(default=0, help_text="Data used in MB")
    max_time = models.IntegerField(help_text="Maximum time in minutes", default=0)
    max_data = models.IntegerField(help_text="Maximum data in MB", default=0)
    
    # Expiry
    expires_at = models.DateTimeField(default=timezone.now)
    used_at = models.DateTimeField(blank=True, null=True)
    
    # Financial
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='KES')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.username:
            self.username = self.generate_username()
        if not self.password:
            self.password = self.generate_password()
        super().save(*args, **kwargs)
    
    def generate_code(self):
        """Generate unique ticket code"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            if not Ticket.objects.filter(code=code).exists():
                return code
    
    def generate_username(self):
        """Generate unique username"""
        while True:
            username = f"user{secrets.randbelow(9999):04d}"
            if not Ticket.objects.filter(username=username, provider=self.provider).exists():
                return username
    
    def generate_password(self):
        """Generate random password"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    def is_expired(self):
        """Check if ticket is expired"""
        return timezone.now() > self.expires_at or self.status == 'expired'
    
    def is_used(self):
        """Check if ticket is used"""
        return self.status == 'used' or self.used_at is not None
    
    def can_use(self):
        """Check if ticket can be used"""
        return (
            self.status == 'active' and 
            not self.is_expired() and 
            not self.is_used()
        )
    
    def get_remaining_time(self):
        """Get remaining time in minutes"""
        if self.ticket_type.ticket_type == 'time':
            return max(0, self.max_time - self.time_used)
        return 0
    
    def get_remaining_data(self):
        """Get remaining data in MB"""
        if self.ticket_type.ticket_type == 'data':
            return max(0, self.max_data - self.data_used)
        return 0
    
    def __str__(self):
        return f"{self.code} - {self.ticket_type.name}"


class TicketSale(models.Model):
    """Ticket sales records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='ticket_sales', null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='sales', null=True, blank=True)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    
    # Sale details
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='KES')
    
    # Payment
    payment_method = models.CharField(max_length=50, default='cash')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # Timestamps
    sold_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sold_at']
    
    def __str__(self):
        return f"Sale {self.id} - {self.ticket.code}"


class TicketBatch(models.Model):
    """Batch of tickets generated together"""
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='ticket_batches', null=True, blank=True)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='batches', null=True, blank=True)
    batch_name = models.CharField(max_length=100, default='Batch')
    quantity = models.IntegerField()
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_batches', null=True, blank=True)
    
    # Batch details
    start_code = models.CharField(max_length=20, blank=True, null=True)
    end_code = models.CharField(max_length=20, blank=True, null=True)
    expiry_days = models.IntegerField(default=30)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.batch_name} - {self.quantity} tickets"


class TicketUsage(models.Model):
    """Track ticket usage for analytics"""
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='usage')
    session_start = models.DateTimeField(blank=True, null=True)
    session_end = models.DateTimeField(blank=True, null=True)
    total_session_time = models.IntegerField(default=0, help_text="Total session time in minutes")
    total_data_consumed = models.IntegerField(default=0, help_text="Total data consumed in MB")
    device_info = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Usage - {self.ticket.code}"
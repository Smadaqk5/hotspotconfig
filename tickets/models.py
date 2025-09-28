from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import secrets
import string

class TicketType(models.Model):
    """Ticket type definitions for providers"""
    TYPE_CHOICES = [
        ('time', 'Time-based'),
        ('data', 'Data-based'),
    ]
    
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100, help_text="e.g., '1 Hour WiFi', '24 Hours WiFi'")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='time')
    
    # Time-based tickets
    duration_hours = models.IntegerField(blank=True, null=True, help_text="Duration in hours for time-based tickets")
    
    # Data-based tickets  
    data_limit_mb = models.IntegerField(blank=True, null=True, help_text="Data limit in MB for data-based tickets")
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    currency = models.CharField(max_length=3, default='KES')
    
    # Bandwidth limits
    download_speed_mbps = models.IntegerField(default=5, help_text="Download speed limit in Mbps")
    upload_speed_mbps = models.IntegerField(default=2, help_text="Upload speed limit in Mbps")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show prominently in captive portal")
    
    # Metadata
    description = models.TextField(blank=True, help_text="Description shown to customers")
    icon = models.CharField(max_length=50, default='fas fa-wifi', help_text="Font Awesome icon class")
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color for UI")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
        unique_together = ['provider', 'name']
    
    def __str__(self):
        return f"{self.provider.business_name} - {self.name}"
    
    def get_display_name(self):
        """Get display name for captive portal"""
        if self.type == 'time':
            return f"{self.duration_hours}h WiFi - Ksh {self.price}"
        else:
            return f"{self.data_limit_mb}MB WiFi - Ksh {self.price}"
    
    def get_duration_display(self):
        """Get human-readable duration"""
        if self.type == 'time':
            if self.duration_hours == 1:
                return "1 Hour"
            elif self.duration_hours < 24:
                return f"{self.duration_hours} Hours"
            else:
                days = self.duration_hours // 24
                hours = self.duration_hours % 24
                if hours == 0:
                    return f"{days} Day{'s' if days > 1 else ''}"
                else:
                    return f"{days} Day{'s' if days > 1 else ''} {hours}h"
        else:
            if self.data_limit_mb < 1024:
                return f"{self.data_limit_mb} MB"
            else:
                gb = self.data_limit_mb / 1024
                return f"{gb:.1f} GB"

class Ticket(models.Model):
    """Individual tickets/vouchers"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='tickets')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='tickets')
    
    # Ticket details
    code = models.CharField(max_length=20, unique=True, help_text="Unique ticket code")
    username = models.CharField(max_length=50, help_text="Username for hotspot login")
    password = models.CharField(max_length=50, help_text="Password for hotspot login")
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)
    
    # Usage tracking
    device_mac = models.CharField(max_length=17, blank=True, help_text="MAC address of connected device")
    device_ip = models.GenericIPAddressField(blank=True, null=True, help_text="IP address of connected device")
    session_start = models.DateTimeField(blank=True, null=True)
    session_end = models.DateTimeField(blank=True, null=True)
    
    # Data usage (for data-based tickets)
    data_used_mb = models.IntegerField(default=0, help_text="Data used in MB")
    
    # Payment reference
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, blank=True, null=True, related_name='tickets')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Ticket {self.code} - {self.ticket_type.name}"
    
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
            username = f"user{secrets.randbelow(999999):06d}"
            if not Ticket.objects.filter(username=username).exists():
                return username
    
    def generate_password(self):
        """Generate random password"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    def is_expired(self):
        """Check if ticket is expired"""
        return timezone.now() > self.expires_at
    
    def is_used(self):
        """Check if ticket is used"""
        return self.status == 'used'
    
    def can_be_used(self):
        """Check if ticket can be used"""
        return self.status == 'active' and not self.is_expired()
    
    def get_remaining_time(self):
        """Get remaining time in hours"""
        if self.ticket_type.type == 'time':
            if self.is_expired():
                return 0
            remaining = self.expires_at - timezone.now()
            return max(0, remaining.total_seconds() / 3600)
        return None
    
    def get_remaining_data(self):
        """Get remaining data in MB"""
        if self.ticket_type.type == 'data':
            return max(0, self.ticket_type.data_limit_mb - self.data_used_mb)
        return None
    
    def activate(self, device_mac=None, device_ip=None):
        """Activate ticket for use"""
        if not self.can_be_used():
            return False
        
        self.status = 'used'
        self.used_at = timezone.now()
        self.session_start = timezone.now()
        if device_mac:
            self.device_mac = device_mac
        if device_ip:
            self.device_ip = device_ip
        self.save()
        return True
    
    def deactivate(self):
        """Deactivate ticket"""
        self.session_end = timezone.now()
        self.save()
    
    def update_data_usage(self, mb_used):
        """Update data usage for data-based tickets"""
        if self.ticket_type.type == 'data':
            self.data_used_mb += mb_used
            if self.data_used_mb >= self.ticket_type.data_limit_mb:
                self.status = 'expired'
            self.save()

class TicketSale(models.Model):
    """Sales records for tickets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='ticket_sales')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='sales')
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='sale')
    
    # Sale details
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    
    # Payment details
    payment_method = models.CharField(max_length=50, default='mpesa')
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Sale {self.id} - {self.ticket_type.name}"
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)

class TicketUsage(models.Model):
    """Track ticket usage sessions"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='usage_sessions')
    session_start = models.DateTimeField()
    session_end = models.DateTimeField(blank=True, null=True)
    device_mac = models.CharField(max_length=17)
    device_ip = models.GenericIPAddressField()
    data_used_mb = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-session_start']
    
    def __str__(self):
        return f"Usage {self.ticket.code} - {self.session_start}"
    
    def get_duration(self):
        """Get session duration in minutes"""
        if self.session_end:
            duration = self.session_end - self.session_start
            return duration.total_seconds() / 60
        else:
            duration = timezone.now() - self.session_start
            return duration.total_seconds() / 60
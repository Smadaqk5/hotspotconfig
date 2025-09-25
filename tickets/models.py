"""
Ticket/Voucher Models for MikroTik Hotspot Ticketing System
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import secrets
import string

User = get_user_model()


class TicketType(models.Model):
    """Types of tickets (time-based, data-based)"""
    
    TYPE_CHOICES = [
        ('time', 'Time-based'),
        ('data', 'Data-based'),
        ('unlimited', 'Unlimited'),
    ]
    
    name = models.CharField(max_length=100, help_text="Ticket type name (e.g., '1 Hour', '1GB Data')")
    ticket_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='time')
    description = models.TextField(blank=True, help_text="Description of the ticket type")
    
    # For time-based tickets
    duration_hours = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Duration in hours for time-based tickets",
        validators=[MinValueValidator(1), MaxValueValidator(8760)]  # Max 1 year
    )
    
    # For data-based tickets
    data_limit_gb = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Data limit in GB for data-based tickets",
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in KES"
    )
    currency = models.CharField(max_length=3, default='KES')
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, help_text="Mark as popular ticket type")
    sort_order = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Admin who created this ticket type"
    )
    
    class Meta:
        ordering = ['sort_order', 'price']
        verbose_name = "Ticket Type"
        verbose_name_plural = "Ticket Types"
    
    def __str__(self):
        return f"{self.name} - {self.currency} {self.price}"
    
    @property
    def duration_display(self):
        """Display duration in human readable format"""
        if self.ticket_type == 'time' and self.duration_hours:
            if self.duration_hours < 24:
                return f"{self.duration_hours} hour{'s' if self.duration_hours > 1 else ''}"
            elif self.duration_hours < 168:  # 7 days
                days = self.duration_hours // 24
                return f"{days} day{'s' if days > 1 else ''}"
            else:
                weeks = self.duration_hours // 168
                return f"{weeks} week{'s' if weeks > 1 else ''}"
        elif self.ticket_type == 'data' and self.data_limit_gb:
            return f"{self.data_limit_gb}GB"
        elif self.ticket_type == 'unlimited':
            return "Unlimited"
        return "N/A"
    
    @property
    def price_display(self):
        """Display price with currency"""
        return f"{self.currency} {self.price}"


class Ticket(models.Model):
    """Individual tickets/vouchers"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    
    # Ticket credentials
    username = models.CharField(max_length=50, help_text="Username for the ticket")
    password = models.CharField(max_length=20, help_text="Password/PIN for the ticket")
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True, help_text="When the ticket was first used")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When the ticket expires")
    
    # Usage tracking
    data_used_bytes = models.BigIntegerField(default=0, help_text="Data used in bytes")
    time_used_seconds = models.BigIntegerField(default=0, help_text="Time used in seconds")
    
    # MikroTik integration
    mikrotik_username = models.CharField(max_length=50, blank=True, help_text="Username in MikroTik")
    mikrotik_profile = models.CharField(max_length=100, blank=True, help_text="MikroTik profile name")
    is_synced_to_router = models.BooleanField(default=False, help_text="Whether synced to MikroTik router")
    
    # Additional info
    notes = models.TextField(blank=True, help_text="Additional notes about this ticket")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username', 'password']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.ticket_type.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Generate username and password if not provided
        if not self.username:
            self.username = self.generate_username()
        if not self.password:
            self.password = self.generate_password()
        
        # Set expiry date based on ticket type
        if not self.expires_at and self.ticket_type.ticket_type == 'time':
            if self.ticket_type.duration_hours:
                self.expires_at = timezone.now() + timezone.timedelta(hours=self.ticket_type.duration_hours)
        
        super().save(*args, **kwargs)
    
    def generate_username(self):
        """Generate a unique username"""
        prefix = self.ticket_type.name.replace(' ', '').lower()[:3]
        random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(5))
        return f"{prefix}{random_part}"
    
    def generate_password(self):
        """Generate a secure password"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    def is_expired(self):
        """Check if ticket is expired"""
        if self.status in ['used', 'expired', 'cancelled']:
            return True
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False
    
    def is_used(self):
        """Check if ticket has been used"""
        return self.status == 'used' or self.activated_at is not None
    
    def get_remaining_data(self):
        """Get remaining data in GB"""
        if self.ticket_type.ticket_type != 'data' or not self.ticket_type.data_limit_gb:
            return None
        used_gb = self.data_used_bytes / (1024 ** 3)
        remaining = self.ticket_type.data_limit_gb - used_gb
        return max(0, remaining)
    
    def get_remaining_time(self):
        """Get remaining time in hours"""
        if self.ticket_type.ticket_type != 'time' or not self.ticket_type.duration_hours:
            return None
        used_hours = self.time_used_seconds / 3600
        remaining = self.ticket_type.duration_hours - used_hours
        return max(0, remaining)
    
    def activate(self):
        """Activate the ticket"""
        if self.status == 'active' and not self.activated_at:
            self.activated_at = timezone.now()
            self.status = 'used'
            self.save()
    
    def expire(self):
        """Mark ticket as expired"""
        if self.status == 'active':
            self.status = 'expired'
            self.save()


class TicketSale(models.Model):
    """Track ticket sales and revenue"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
        ('pesapal', 'Pesapal'),
        ('other', 'Other'),
    ]
    
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='sale')
    sold_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_sales')
    sold_at = models.DateTimeField(auto_now_add=True)
    
    # Sale details
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Actual sale price")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_reference = models.CharField(max_length=100, blank=True, help_text="Payment reference number")
    
    # Customer info
    customer_name = models.CharField(max_length=100, blank=True)
    customer_phone = models.CharField(max_length=15, blank=True)
    customer_email = models.EmailField(blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-sold_at']
    
    def __str__(self):
        return f"Sale of {self.ticket.username} - {self.sale_price} {self.ticket.ticket_type.currency}"


class TicketBatch(models.Model):
    """Batch creation of tickets"""
    
    name = models.CharField(max_length=200, help_text="Batch name")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='batches')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_batches')
    
    # Batch configuration
    quantity = models.PositiveIntegerField(help_text="Number of tickets to generate")
    username_prefix = models.CharField(max_length=10, blank=True, help_text="Prefix for usernames")
    password_length = models.PositiveIntegerField(default=6, help_text="Password length")
    
    # Status
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.quantity} tickets"
    
    def generate_tickets(self):
        """Generate tickets for this batch"""
        if self.is_generated:
            return
        
        for i in range(self.quantity):
            username = f"{self.username_prefix}{i+1:04d}" if self.username_prefix else None
            Ticket.objects.create(
                ticket_type=self.ticket_type,
                user=self.user,
                username=username,
                password=''.join(secrets.choice(string.digits) for _ in range(self.password_length))
            )
        
        self.is_generated = True
        self.generated_at = timezone.now()
        self.save()


class TicketUsage(models.Model):
    """Track ticket usage for analytics"""
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='usage_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Usage data
    data_used_bytes = models.BigIntegerField(default=0)
    time_used_seconds = models.BigIntegerField(default=0)
    
    # Connection info
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Usage of {self.ticket.username} at {self.timestamp}"
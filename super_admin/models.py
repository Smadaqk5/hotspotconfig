from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SystemSettings(models.Model):
    """Global system settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    data_type = models.CharField(max_length=20, default='string', choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ])
    is_public = models.BooleanField(default=False, help_text="Can be accessed by providers")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return f"{self.key} = {self.value}"
    
    def get_typed_value(self):
        """Get value with proper type conversion"""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.data_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class PlatformAnalytics(models.Model):
    """Platform-wide analytics"""
    date = models.DateField(unique=True)
    
    # Provider metrics
    total_providers = models.IntegerField(default=0)
    active_providers = models.IntegerField(default=0)
    new_providers = models.IntegerField(default=0)
    
    # Ticket metrics
    total_tickets_generated = models.IntegerField(default=0)
    total_tickets_sold = models.IntegerField(default=0)
    total_tickets_active = models.IntegerField(default=0)
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    platform_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    provider_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # User metrics
    total_end_users = models.IntegerField(default=0)
    active_end_users = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Platform Analytics'
        verbose_name_plural = 'Platform Analytics'
    
    def __str__(self):
        return f"Analytics - {self.date}"


class ProviderCommission(models.Model):
    """Commission structure for providers"""
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='commissions')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission rate as percentage")
    min_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.provider.business_name} - {self.commission_rate}%"


class SystemNotification(models.Model):
    """System-wide notifications"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False, help_text="Show to all users")
    target_providers = models.ManyToManyField('accounts.Provider', blank=True, related_name='notifications')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

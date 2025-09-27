from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class ProviderSubscriptionPlan(models.Model):
    """Subscription plans for providers"""
    PLAN_TYPES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    duration_days = models.IntegerField(help_text="Duration in days")
    
    # Features
    max_tickets_per_month = models.IntegerField(default=1000)
    max_locations = models.IntegerField(default=1)
    max_end_users = models.IntegerField(default=100)
    api_access = models.BooleanField(default=False)
    custom_branding = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    advanced_analytics = models.BooleanField(default=False)
    
    # Limits
    max_ticket_types = models.IntegerField(default=10)
    max_config_templates = models.IntegerField(default=5)
    storage_limit_gb = models.IntegerField(default=1)
    
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'price']
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"
    
    def get_features_list(self):
        """Get list of features as strings"""
        features = []
        if self.max_tickets_per_month:
            features.append(f"Up to {self.max_tickets_per_month} tickets/month")
        if self.max_locations:
            features.append(f"Up to {self.max_locations} locations")
        if self.api_access:
            features.append("API Access")
        if self.custom_branding:
            features.append("Custom Branding")
        if self.priority_support:
            features.append("Priority Support")
        if self.advanced_analytics:
            features.append("Advanced Analytics")
        return features


class ProviderSubscription(models.Model):
    """Provider subscriptions"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey('accounts.Provider', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(ProviderSubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Subscription period
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=False)
    
    # Payment
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    payment_method = models.CharField(max_length=50, default='pesapal')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Usage tracking
    tickets_generated = models.IntegerField(default=0)
    tickets_sold = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Admin
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_subscriptions')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if subscription is expired"""
        return timezone.now() > self.end_date or self.status == 'expired'
    
    def is_active(self):
        """Check if subscription is active"""
        return (
            self.status == 'active' and 
            not self.is_expired() and
            self.provider.is_active()
        )
    
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.is_expired():
            return 0
        return (self.end_date - timezone.now()).days
    
    def get_usage_percentage(self):
        """Get usage percentage for tickets"""
        if self.plan.max_tickets_per_month == 0:
            return 0
        return (self.tickets_generated / self.plan.max_tickets_per_month) * 100
    
    def can_generate_tickets(self, quantity=1):
        """Check if provider can generate more tickets"""
        return (self.tickets_generated + quantity) <= self.plan.max_tickets_per_month
    
    def __str__(self):
        return f"{self.provider.business_name} - {self.plan.name}"


class SubscriptionUsage(models.Model):
    """Track subscription usage"""
    subscription = models.OneToOneField(ProviderSubscription, on_delete=models.CASCADE, related_name='usage_tracking')
    
    # Monthly counters
    current_month_tickets = models.IntegerField(default=0)
    current_month_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_month_users = models.IntegerField(default=0)
    
    # All-time counters
    total_tickets_generated = models.IntegerField(default=0)
    total_tickets_sold = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_end_users = models.IntegerField(default=0)
    
    # Last reset
    last_reset_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def reset_monthly_counters(self):
        """Reset monthly counters"""
        self.current_month_tickets = 0
        self.current_month_revenue = 0
        self.current_month_users = 0
        self.last_reset_date = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Usage - {self.subscription.provider.business_name}"


class SubscriptionPayment(models.Model):
    """Subscription payment records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(ProviderSubscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment details
    payment_method = models.CharField(max_length=50, default='pesapal')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency}"


class SubscriptionFeature(models.Model):
    """Individual features for subscription plans"""
    plan = models.ForeignKey(ProviderSubscriptionPlan, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_included = models.BooleanField(default=True)
    limit_value = models.IntegerField(blank=True, null=True, help_text="Limit value if applicable")
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.plan.name} - {self.name}"
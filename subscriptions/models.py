from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Subscription plans available"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()  # Duration in days
    is_active = models.BooleanField(default=True)
    features = models.JSONField(default=list)  # List of features included
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """User subscriptions"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.end_date
    
    def days_remaining(self):
        if self.is_expired():
            return 0
        return (self.end_date - timezone.now()).days
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    class Meta:
        ordering = ['-created_at']


class SubscriptionUsage(models.Model):
    """Track subscription usage"""
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='usage')
    configs_generated = models.IntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subscription.user.email} - {self.configs_generated} configs"

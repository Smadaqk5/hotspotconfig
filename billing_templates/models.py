"""
Billing Templates Models for MikroTik Hotspot Config Generator
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class BillingTemplate(models.Model):
    """Billing template for bandwidth and duration configuration"""
    
    DURATION_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('hourly', 'Hourly'),
    ]
    
    name = models.CharField(max_length=100, help_text="Template name (e.g., 'Basic Daily Plan')")
    description = models.TextField(blank=True, help_text="Description of the billing template")
    
    # Bandwidth configuration
    mbps = models.PositiveIntegerField(
        help_text="Bandwidth in Mbps",
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    upload_mbps = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Upload bandwidth in Mbps (optional, defaults to download speed)",
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    
    # Duration configuration
    duration_type = models.CharField(
        max_length=20,
        choices=DURATION_CHOICES,
        default='daily',
        help_text="Duration type (daily, weekly, monthly, hourly)"
    )
    duration_value = models.PositiveIntegerField(
        default=1,
        help_text="Duration value (e.g., 1 for 1 day, 7 for 7 days)"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in KES"
    )
    currency = models.CharField(max_length=3, default='KES', help_text="Currency code")
    
    # Template configuration
    is_active = models.BooleanField(default=True, help_text="Whether this template is active")
    is_popular = models.BooleanField(default=False, help_text="Mark as popular plan")
    sort_order = models.PositiveIntegerField(default=0, help_text="Sort order for display")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Admin who created this template"
    )
    
    class Meta:
        ordering = ['sort_order', 'price']
        verbose_name = "Billing Template"
        verbose_name_plural = "Billing Templates"
    
    def __str__(self):
        return f"{self.name} - {self.mbps}Mbps {self.duration_type}"
    
    @property
    def duration_display(self):
        """Display duration in human readable format"""
        if self.duration_value == 1:
            return self.get_duration_type_display()
        return f"{self.duration_value} {self.get_duration_type_display()}s"
    
    @property
    def bandwidth_display(self):
        """Display bandwidth in human readable format"""
        if self.upload_mbps:
            return f"{self.mbps}Mbps down / {self.upload_mbps}Mbps up"
        return f"{self.mbps}Mbps"
    
    @property
    def price_display(self):
        """Display price with currency"""
        return f"{self.currency} {self.price}"
    
    def get_duration_seconds(self):
        """Get duration in seconds for MikroTik configuration"""
        duration_map = {
            'hourly': 3600,
            'daily': 86400,
            'weekly': 604800,
            'monthly': 2592000,  # 30 days
        }
        return duration_map.get(self.duration_type, 86400) * self.duration_value
    
    def get_bandwidth_bytes(self):
        """Get bandwidth in bytes per second for MikroTik configuration"""
        return self.mbps * 1024 * 1024  # Convert Mbps to bytes per second
    
    def get_upload_bandwidth_bytes(self):
        """Get upload bandwidth in bytes per second for MikroTik configuration"""
        if self.upload_mbps:
            return self.upload_mbps * 1024 * 1024
        return self.get_bandwidth_bytes()


class BillingTemplateUsage(models.Model):
    """Track usage of billing templates"""
    
    template = models.ForeignKey(
        BillingTemplate,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='billing_template_usage'
    )
    generated_config = models.ForeignKey(
        'config_generator.GeneratedConfig',
        on_delete=models.CASCADE,
        related_name='billing_template_usage'
    )
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-used_at']
        verbose_name = "Billing Template Usage"
        verbose_name_plural = "Billing Template Usage Records"
    
    def __str__(self):
        return f"{self.user.email} used {self.template.name} on {self.used_at}"


class BillingTemplateCategory(models.Model):
    """Categories for organizing billing templates"""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hex color code for category display"
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Billing Template Category"
        verbose_name_plural = "Billing Template Categories"
    
    def __str__(self):
        return self.name


class BillingTemplateCategoryAssignment(models.Model):
    """Assign templates to categories"""
    
    template = models.ForeignKey(
        BillingTemplate,
        on_delete=models.CASCADE,
        related_name='category_assignments'
    )
    category = models.ForeignKey(
        BillingTemplateCategory,
        on_delete=models.CASCADE,
        related_name='template_assignments'
    )
    
    class Meta:
        unique_together = ['template', 'category']
        verbose_name = "Template Category Assignment"
        verbose_name_plural = "Template Category Assignments"
    
    def __str__(self):
        return f"{self.template.name} in {self.category.name}"

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class MikroTikModel(models.Model):
    """MikroTik router models"""
    name = models.CharField(max_length=100)
    model_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class VoucherType(models.Model):
    """Voucher types (daily, weekly, monthly)"""
    name = models.CharField(max_length=50)
    duration_hours = models.IntegerField()  # Duration in hours
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class BandwidthProfile(models.Model):
    """Bandwidth profiles for vouchers"""
    name = models.CharField(max_length=100)
    download_speed = models.CharField(max_length=20)  # e.g., "10M"
    upload_speed = models.CharField(max_length=20)   # e.g., "5M"
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.download_speed}/{self.upload_speed})"


class ConfigTemplate(models.Model):
    """MikroTik configuration templates"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    mikrotik_model = models.ForeignKey(MikroTikModel, on_delete=models.CASCADE)
    template_content = models.TextField()  # Jinja2 template
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.mikrotik_model.name}"


class GeneratedConfig(models.Model):
    """Generated configuration files"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_configs')
    template = models.ForeignKey(ConfigTemplate, on_delete=models.CASCADE)
    config_name = models.CharField(max_length=200)
    config_content = models.TextField()
    
    # Configuration parameters
    hotspot_name = models.CharField(max_length=100)
    hotspot_ip = models.GenericIPAddressField()
    dns_servers = models.CharField(max_length=200)  # Comma-separated DNS servers
    voucher_type = models.ForeignKey(VoucherType, on_delete=models.CASCADE)
    bandwidth_profile = models.ForeignKey(BandwidthProfile, on_delete=models.CASCADE)
    
    # Additional settings
    max_users = models.IntegerField(default=50)
    voucher_length = models.IntegerField(default=8)  # Voucher code length
    voucher_prefix = models.CharField(max_length=10, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.config_name}"
    
    class Meta:
        ordering = ['-created_at']

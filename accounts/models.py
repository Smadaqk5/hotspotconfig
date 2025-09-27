from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Extended user model with additional fields"""
    USER_TYPE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('provider', 'Provider'),
        ('cashier', 'Cashier/Operator'),
        ('end_user', 'End User'),
    ]
    
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    company_name = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='end_user')
    
    # Provider-specific fields
    provider_license = models.CharField(max_length=100, blank=True, null=True)
    business_registration = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    
    # Super Admin fields
    is_super_admin = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'accounts_user'
    
    def __str__(self):
        return self.email
    
    def is_provider(self):
        return self.user_type == 'provider' or self.is_super_admin
    
    def is_super_admin_user(self):
        return self.user_type == 'super_admin' or self.is_super_admin
    
    def is_cashier(self):
        return self.user_type == 'cashier'
    
    def is_provider_or_cashier(self):
        return self.user_type in ['provider', 'cashier'] or self.is_super_admin
    
    def can_manage_revenue(self):
        """Check if user can view revenue reports"""
        return self.user_type in ['provider', 'super_admin'] or self.is_super_admin
    
    def can_manage_router_configs(self):
        """Check if user can manage router configurations"""
        return self.user_type in ['provider', 'super_admin'] or self.is_super_admin
    
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.user_type in ['provider', 'super_admin'] or self.is_super_admin


class UserProfile(models.Model):
    """User profile with additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Provider-specific profile fields
    business_type = models.CharField(max_length=100, blank=True, null=True)
    years_in_business = models.IntegerField(blank=True, null=True)
    number_of_locations = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Profile"


class Provider(models.Model):
    """Provider model for hotspot operators"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Approval'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    license_number = models.CharField(max_length=100, unique=True)
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact information
    contact_person = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    
    # Business details
    address = models.TextField()
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Kenya')
    
    # Service details
    service_areas = models.TextField(help_text="Areas where the provider offers hotspot services")
    number_of_locations = models.IntegerField(default=1)
    estimated_monthly_users = models.IntegerField(default=100)
    
    # Financial information
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account = models.CharField(max_length=100, blank=True, null=True)
    mpesa_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Subscription and billing
    subscription_status = models.CharField(max_length=20, default='inactive')
    subscription_start_date = models.DateTimeField(blank=True, null=True)
    subscription_end_date = models.DateTimeField(blank=True, null=True)
    
    # Approval and verification
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_providers')
    approved_at = models.DateTimeField(blank=True, null=True)
    
    # Documents
    business_license = models.FileField(upload_to='documents/business_licenses/', blank=True, null=True)
    tax_certificate = models.FileField(upload_to='documents/tax_certificates/', blank=True, null=True)
    id_copy = models.FileField(upload_to='documents/id_copies/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business_name} - {self.user.email}"
    
    def is_active(self):
        return self.status == 'active' and self.is_approved
    
    def get_subscription_status(self):
        if not self.subscription_start_date or not self.subscription_end_date:
            return 'inactive'
        
        if timezone.now() > self.subscription_end_date:
            return 'expired'
        elif timezone.now() >= self.subscription_start_date:
            return 'active'
        else:
            return 'pending'


class EndUser(models.Model):
    """End user model for hotspot customers"""
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='end_users')
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['provider', 'username']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} - {self.provider.business_name}"


class SuperAdmin(models.Model):
    """Super admin model for platform administrators"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='super_admin_profile')
    permissions = models.JSONField(default=list, help_text="List of specific permissions")
    can_manage_providers = models.BooleanField(default=True)
    can_view_analytics = models.BooleanField(default=True)
    can_manage_system = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Super Admin - {self.user.email}"


class Cashier(models.Model):
    """Cashier/Operator model for provider employees"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cashier_profile')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='cashiers')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Permissions
    can_generate_tickets = models.BooleanField(default=True)
    can_sell_tickets = models.BooleanField(default=True)
    can_view_sales = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_download_configs = models.BooleanField(default=False)
    
    # Work details
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    shift_hours = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cashier - {self.user.email} ({self.provider.business_name})"
    
    def is_active(self):
        return self.status == 'active'
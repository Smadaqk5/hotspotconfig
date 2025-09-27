from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Provider, EndUser, SuperAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_staff')
    list_filter = ('is_verified', 'is_staff', 'is_superuser', 'is_active', 'user_type', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'company_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'company_name', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
        ('Verification', {'fields': ('is_verified',)}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_type', 'website', 'created_at')
    search_fields = ('user__email', 'user__username', 'business_type')
    list_filter = ('business_type', 'created_at')
    raw_id_fields = ('user',)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'status', 'is_approved', 'created_at')
    list_filter = ('status', 'is_approved', 'created_at')
    search_fields = ('user__email', 'business_name', 'license_number')
    raw_id_fields = ('user', 'approved_by')
    readonly_fields = ('created_at', 'updated_at', 'approved_at')


@admin.register(EndUser)
class EndUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'provider', 'is_active', 'created_at')
    list_filter = ('provider', 'is_active', 'created_at')
    search_fields = ('username', 'provider__business_name')
    raw_id_fields = ('provider',)


@admin.register(SuperAdmin)
class SuperAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'can_manage_providers', 'can_view_analytics', 'created_at')
    list_filter = ('can_manage_providers', 'can_view_analytics', 'created_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)

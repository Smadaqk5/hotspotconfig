from django.contrib import admin
from .models import SystemSettings, PlatformAnalytics, ProviderCommission, SystemNotification


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'data_type', 'is_public', 'updated_at')
    list_filter = ('data_type', 'is_public')
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Setting Details', {
            'fields': ('key', 'value', 'description', 'data_type', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_providers', 'active_providers', 'total_revenue', 'platform_revenue')
    list_filter = ('date',)
    search_fields = ('date',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date',)
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Provider Metrics', {
            'fields': ('total_providers', 'active_providers', 'new_providers')
        }),
        ('Ticket Metrics', {
            'fields': ('total_tickets_generated', 'total_tickets_sold', 'total_tickets_active')
        }),
        ('Revenue Metrics', {
            'fields': ('total_revenue', 'platform_revenue', 'provider_revenue')
        }),
        ('User Metrics', {
            'fields': ('total_end_users', 'active_end_users')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProviderCommission)
class ProviderCommissionAdmin(admin.ModelAdmin):
    list_display = ('provider', 'commission_rate', 'min_commission', 'max_commission', 'is_active')
    list_filter = ('is_active', 'commission_rate')
    search_fields = ('provider__business_name', 'provider__user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Commission Details', {
            'fields': ('provider', 'commission_rate', 'min_commission', 'max_commission', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'is_active', 'is_global', 'created_at')
    list_filter = ('notification_type', 'is_active', 'is_global', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('target_providers',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('title', 'message', 'notification_type', 'is_active')
        }),
        ('Targeting', {
            'fields': ('is_global', 'target_providers')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

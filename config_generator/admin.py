from django.contrib import admin
from .models import MikroTikModel, VoucherType, BandwidthProfile, ConfigTemplate, GeneratedConfig


@admin.register(MikroTikModel)
class MikroTikModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'model_code', 'description')
    ordering = ('name',)


@admin.register(VoucherType)
class VoucherTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_hours', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('duration_hours',)


@admin.register(BandwidthProfile)
class BandwidthProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'download_speed', 'upload_speed', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(ConfigTemplate)
class ConfigTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'mikrotik_model', 'is_active', 'created_at')
    list_filter = ('is_active', 'mikrotik_model', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Template Details', {
            'fields': ('name', 'description', 'mikrotik_model', 'is_active')
        }),
        ('Template Content', {
            'fields': ('template_content',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GeneratedConfig)
class GeneratedConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'config_name', 'hotspot_name', 'voucher_type', 'bandwidth_profile', 'created_at')
    list_filter = ('voucher_type', 'bandwidth_profile', 'created_at')
    search_fields = ('user__email', 'config_name', 'hotspot_name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Config Details', {
            'fields': ('user', 'template', 'config_name', 'hotspot_name', 'hotspot_ip')
        }),
        ('Configuration', {
            'fields': ('dns_servers', 'voucher_type', 'bandwidth_profile', 'max_users', 'voucher_length', 'voucher_prefix')
        }),
        ('Generated Content', {
            'fields': ('config_content',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

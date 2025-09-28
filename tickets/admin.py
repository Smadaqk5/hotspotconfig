"""
Admin interface for tickets app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    TicketType, Ticket, TicketSale, TicketUsage
)


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'type', 'duration_hours', 'data_limit_mb', 'price', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'provider__business_name']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'name', 'type', 'description', 'is_active', 'is_featured')
        }),
        ('Time Configuration', {
            'fields': ('duration_hours',),
            'description': 'Duration in hours for time-based tickets'
        }),
        ('Data Configuration', {
            'fields': ('data_limit_mb',),
            'description': 'Data limit in MB for data-based tickets'
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Bandwidth Limits', {
            'fields': ('download_speed_mbps', 'upload_speed_mbps')
        }),
        ('Display', {
            'fields': ('icon', 'color')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provider')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'provider', 'ticket_type', 'status', 'created_at', 
        'expires_at', 'data_used_mb'
    ]
    list_filter = [
        'status', 'ticket_type__type', 'created_at', 'expires_at'
    ]
    search_fields = ['code', 'username', 'provider__business_name']
    list_editable = ['status']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('provider', 'ticket_type', 'code', 'username', 'password', 'status')
        }),
        ('Timing', {
            'fields': ('created_at', 'used_at', 'expires_at')
        }),
        ('Usage Tracking', {
            'fields': ('device_mac', 'device_ip', 'session_start', 'session_end', 'data_used_mb'),
            'classes': ('collapse',)
        }),
        ('Payment', {
            'fields': ('payment',)
        })
    )
    
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket_type', 'provider')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing ticket
            return self.readonly_fields + ['code', 'username', 'password']
        return self.readonly_fields


@admin.register(TicketSale)
class TicketSaleAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'provider', 'unit_price', 'total_amount', 
        'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'ticket__code', 'payment_reference'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('provider', 'ticket_type', 'ticket', 'quantity', 'unit_price', 'total_amount', 'currency')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_reference', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'provider')


@admin.register(TicketUsage)
class TicketUsageAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'session_start', 'session_end', 'data_used_mb', 
        'device_ip', 'created_at'
    ]
    list_filter = ['created_at', 'ticket__ticket_type__type']
    search_fields = ['ticket__code', 'device_ip', 'device_mac']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('ticket', 'session_start', 'session_end', 'data_used_mb')
        }),
        ('Connection Info', {
            'fields': ('device_mac', 'device_ip'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'ticket__ticket_type')


# Custom admin actions
@admin.action(description='Activate selected tickets')
def activate_tickets(modeladmin, request, queryset):
    """Activate selected tickets"""
    count = 0
    for ticket in queryset.filter(status='active'):
        if ticket.activate():
            count += 1
    modeladmin.message_user(request, f'{count} tickets activated.')

# Add actions to TicketAdmin
TicketAdmin.actions = [activate_tickets]
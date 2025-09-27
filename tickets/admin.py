"""
Admin interface for tickets app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    TicketType, Ticket, TicketSale, TicketBatch, TicketUsage
)


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'ticket_type', 'value', 'price', 'is_active', 'created_at']
    list_filter = ['ticket_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'provider__business_name']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'name', 'ticket_type', 'description', 'is_active')
        }),
        ('Configuration', {
            'fields': ('value',),
            'description': 'Value in hours for time-based, or GB for data-based'
        }),
        ('Pricing', {
            'fields': ('price',)
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
        'expires_at', 'price'
    ]
    list_filter = [
        'status', 'ticket_type', 'created_at', 'expires_at'
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
            'fields': ('time_used', 'data_used', 'max_time', 'max_data'),
            'classes': ('collapse',)
        }),
        ('Financial', {
            'fields': ('price', 'currency')
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket_type', 'provider')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing ticket
            return self.readonly_fields + ['code', 'username', 'password']
        return self.readonly_fields


@admin.register(TicketSale)
class TicketSaleAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'provider', 'customer_name', 'unit_price', 'total_amount', 
        'status', 'sold_at'
    ]
    list_filter = ['status', 'payment_method', 'sold_at']
    search_fields = [
        'ticket__code', 'customer_name', 'customer_phone', 
        'customer_email', 'payment_reference'
    ]
    ordering = ['-sold_at']
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('provider', 'ticket', 'quantity', 'unit_price', 'total_amount', 'currency')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_reference', 'status')
        }),
        ('Timestamps', {
            'fields': ('sold_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['sold_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'provider')


@admin.register(TicketBatch)
class TicketBatchAdmin(admin.ModelAdmin):
    list_display = [
        'batch_name', 'provider', 'ticket_type', 'quantity', 'generated_by', 
        'created_at'
    ]
    list_filter = ['ticket_type', 'created_at']
    search_fields = ['batch_name', 'provider__business_name', 'generated_by__email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Batch Information', {
            'fields': ('provider', 'ticket_type', 'batch_name', 'quantity', 'generated_by')
        }),
        ('Configuration', {
            'fields': ('start_code', 'end_code', 'expiry_days')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )
    
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket_type', 'provider', 'generated_by')


@admin.register(TicketUsage)
class TicketUsageAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'session_start', 'total_session_time', 'total_data_consumed', 
        'ip_address', 'created_at'
    ]
    list_filter = ['created_at', 'ticket__ticket_type']
    search_fields = ['ticket__code', 'ip_address']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('ticket', 'session_start', 'session_end', 'total_session_time', 'total_data_consumed')
        }),
        ('Connection Info', {
            'fields': ('ip_address', 'device_info'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'ticket__ticket_type')


# Custom admin actions
@admin.action(description='Activate selected tickets')
def activate_tickets(modeladmin, request, queryset):
    """Activate selected tickets"""
    count = 0
    for ticket in queryset.filter(status='active'):
        ticket.activate()
        count += 1
    modeladmin.message_user(request, f'{count} tickets activated.')

@admin.action(description='Expire selected tickets')
def expire_tickets(modeladmin, request, queryset):
    """Expire selected tickets"""
    count = 0
    for ticket in queryset.filter(status='active'):
        ticket.expire()
        count += 1
    modeladmin.message_user(request, f'{count} tickets expired.')

# Add actions to TicketAdmin
TicketAdmin.actions = [activate_tickets, expire_tickets]
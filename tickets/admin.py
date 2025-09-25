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
    list_display = ['name', 'ticket_type', 'duration_display', 'price_display', 'is_active', 'is_popular', 'sort_order']
    list_filter = ['ticket_type', 'is_active', 'is_popular', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'is_popular', 'sort_order']
    ordering = ['sort_order', 'price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'ticket_type', 'description', 'is_active', 'is_popular', 'sort_order')
        }),
        ('Configuration', {
            'fields': ('duration_hours', 'data_limit_gb'),
            'description': 'Configure based on ticket type'
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'ticket_type', 'user', 'status', 'created_at', 
        'activated_at', 'expires_at', 'is_synced_to_router'
    ]
    list_filter = [
        'status', 'ticket_type', 'is_synced_to_router', 'created_at', 
        'activated_at', 'expires_at'
    ]
    search_fields = ['username', 'password', 'user__email', 'user__username']
    list_editable = ['status']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_type', 'user', 'username', 'password', 'status')
        }),
        ('Timing', {
            'fields': ('created_at', 'activated_at', 'expires_at')
        }),
        ('Usage Tracking', {
            'fields': ('data_used_bytes', 'time_used_seconds'),
            'classes': ('collapse',)
        }),
        ('MikroTik Integration', {
            'fields': ('mikrotik_username', 'mikrotik_profile', 'is_synced_to_router'),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'activated_at', 'data_used_bytes', 'time_used_seconds']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket_type', 'user')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing ticket
            return self.readonly_fields + ['username', 'password']
        return self.readonly_fields


@admin.register(TicketSale)
class TicketSaleAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'sold_by', 'sale_price', 'payment_method', 
        'customer_name', 'sold_at'
    ]
    list_filter = ['payment_method', 'sold_at', 'sold_by']
    search_fields = [
        'ticket__username', 'customer_name', 'customer_phone', 
        'customer_email', 'payment_reference'
    ]
    ordering = ['-sold_at']
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('ticket', 'sold_by', 'sale_price', 'payment_method', 'payment_reference')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Additional Info', {
            'fields': ('notes', 'sold_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['sold_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'sold_by')


@admin.register(TicketBatch)
class TicketBatchAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'ticket_type', 'user', 'quantity', 'is_generated', 
        'generated_at', 'created_at'
    ]
    list_filter = ['is_generated', 'ticket_type', 'created_at']
    search_fields = ['name', 'user__email', 'user__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Batch Information', {
            'fields': ('name', 'ticket_type', 'user', 'quantity')
        }),
        ('Configuration', {
            'fields': ('username_prefix', 'password_length')
        }),
        ('Status', {
            'fields': ('is_generated', 'generated_at', 'created_at')
        })
    )
    
    readonly_fields = ['is_generated', 'generated_at', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket_type', 'user')


@admin.register(TicketUsage)
class TicketUsageAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'timestamp', 'data_used_bytes', 'time_used_seconds', 
        'ip_address'
    ]
    list_filter = ['timestamp', 'ticket__ticket_type']
    search_fields = ['ticket__username', 'ip_address']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('ticket', 'timestamp', 'data_used_bytes', 'time_used_seconds')
        }),
        ('Connection Info', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['timestamp']
    
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
from django.contrib import admin
from .models import Payment, PaymentItem


class PaymentItemInline(admin.TabularInline):
    model = PaymentItem
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('user__email', 'user__username', 'pesapal_order_tracking_id', 'pesapal_merchant_reference')
    readonly_fields = ('id', 'created_at', 'updated_at', 'completed_at')
    inlines = [PaymentItemInline]
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('user', 'amount', 'currency', 'status', 'payment_method', 'description')
        }),
        ('Pesapal Details', {
            'fields': ('pesapal_order_tracking_id', 'pesapal_merchant_reference', 'pesapal_payment_reference'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentItem)
class PaymentItemAdmin(admin.ModelAdmin):
    list_display = ('payment', 'name', 'quantity', 'unit_price', 'total_price')
    list_filter = ('payment__status', 'payment__created_at')
    search_fields = ('payment__user__email', 'name', 'description')
    readonly_fields = ('total_price',)

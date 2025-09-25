from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponseRedirect
from .models import SubscriptionPlan, Subscription, SubscriptionUsage
from .forms import SubscriptionPlanForm, BulkPlanUpdateForm
from .admin_dashboard import SubscriptionDashboard


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    form = SubscriptionPlanForm
    list_display = ('name', 'price', 'duration_days', 'is_active', 'subscriber_count')
    list_filter = ('is_active', 'duration_days')
    search_fields = ('name', 'description')
    ordering = ('price',)
    list_editable = ('price', 'duration_days', 'is_active')
    actions = ['activate_plans', 'deactivate_plans', 'bulk_update_plans']
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'description', 'price', 'duration_days', 'is_active')
        }),
        ('Features', {
            'fields': ('features_text',),
            'description': 'Enter features as a JSON array, e.g., ["Feature 1", "Feature 2"]'
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('price')
    
    def subscriber_count(self, obj):
        """Show number of active subscribers for this plan"""
        return obj.subscription_set.filter(is_active=True, status='active').count()
    subscriber_count.short_description = 'Active Subscribers'
    
    def activate_plans(self, request, queryset):
        """Bulk activate selected plans"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} plans activated successfully.')
    activate_plans.short_description = "Activate selected plans"
    
    def deactivate_plans(self, request, queryset):
        """Bulk deactivate selected plans"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} plans deactivated successfully.')
    deactivate_plans.short_description = "Deactivate selected plans"
    
    def bulk_update_plans(self, request, queryset):
        """Bulk update selected plans"""
        if 'apply' in request.POST:
            form = BulkPlanUpdateForm(request.POST)
            if form.is_valid():
                action = form.cleaned_data['action']
                plans = form.cleaned_data['plans']
                percentage = form.cleaned_data.get('percentage')
                new_duration = form.cleaned_data.get('new_duration')
                
                updated_count = 0
                
                for plan in plans:
                    if action == 'activate':
                        plan.is_active = True
                        plan.save()
                        updated_count += 1
                    elif action == 'deactivate':
                        plan.is_active = False
                        plan.save()
                        updated_count += 1
                    elif action == 'update_price' and percentage:
                        plan.price = plan.price * (1 + percentage / 100)
                        plan.save()
                        updated_count += 1
                    elif action == 'update_duration' and new_duration:
                        plan.duration_days = new_duration
                        plan.save()
                        updated_count += 1
                
                self.message_user(request, f'{updated_count} plans updated successfully.')
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = BulkPlanUpdateForm(initial={'plans': queryset})
        
        return render(request, 'admin/subscriptions/subscriptionplan/bulk_update.html', {
            'form': form,
            'plans': queryset,
            'title': 'Bulk Update Subscription Plans'
        })
    bulk_update_plans.short_description = "Bulk update selected plans"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-update/', self.admin_site.admin_view(self.bulk_update_plans), name='subscriptions_subscriptionplan_bulk_update'),
        ]
        return custom_urls + urls
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Log the change
        from django.contrib.admin.models import LogEntry
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=None,
            object_id=obj.id,
            object_repr=str(obj),
            action_flag=2 if change else 1,
            change_message=f'{"Updated" if change else "Created"} subscription plan: {obj.name}'
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'is_active', 'auto_renew')
    list_filter = ('status', 'is_active', 'auto_renew', 'plan', 'start_date')
    search_fields = ('user__email', 'user__username', 'plan__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'plan', 'status', 'start_date', 'end_date', 'is_active', 'auto_renew')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubscriptionUsage)
class SubscriptionUsageAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'configs_generated', 'last_used')
    list_filter = ('last_used',)
    search_fields = ('subscription__user__email', 'subscription__user__username')
    readonly_fields = ('last_used',)

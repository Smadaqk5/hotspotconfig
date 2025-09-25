"""
Admin configuration for Billing Templates
"""
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import BillingTemplate, BillingTemplateUsage, BillingTemplateCategory, BillingTemplateCategoryAssignment
from .forms import BillingTemplateForm, BillingTemplateCategoryForm, BulkBillingTemplateUpdateForm


@admin.register(BillingTemplateCategory)
class BillingTemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'template_count', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'name')
    list_editable = ('is_active', 'sort_order')
    
    def template_count(self, obj):
        """Show number of templates in this category"""
        return obj.template_assignments.filter(template__is_active=True).count()
    template_count.short_description = 'Active Templates'


@admin.register(BillingTemplate)
class BillingTemplateAdmin(admin.ModelAdmin):
    form = BillingTemplateForm
    list_display = (
        'name', 'bandwidth_display', 'duration_display', 'price_display',
        'is_active', 'is_popular', 'sort_order', 'usage_count', 'created_at'
    )
    list_filter = ('is_active', 'is_popular', 'duration_type')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'price')
    list_editable = ('is_active', 'is_popular', 'sort_order')
    actions = ['activate_templates', 'deactivate_templates', 'mark_popular', 'unmark_popular', 'bulk_update_templates']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'is_active', 'is_popular', 'sort_order')
        }),
        ('Bandwidth Configuration', {
            'fields': ('mbps', 'upload_mbps'),
            'description': 'Configure download and upload speeds in Mbps'
        }),
        ('Duration Configuration', {
            'fields': ('duration_type', 'duration_value'),
            'description': 'Set the duration type and value for this template'
        }),
        ('Pricing', {
            'fields': ('price', 'currency'),
            'description': 'Set the price and currency for this template'
        }),
        ('Metadata', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            usage_count=Count('usage_records')
        ).order_by('sort_order', 'price')
    
    def usage_count(self, obj):
        """Show number of times this template has been used"""
        return obj.usage_count
    usage_count.short_description = 'Usage Count'
    usage_count.admin_order_field = 'usage_count'
    
    def activate_templates(self, request, queryset):
        """Bulk activate selected templates"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} templates activated successfully.')
    activate_templates.short_description = "Activate selected templates"
    
    def deactivate_templates(self, request, queryset):
        """Bulk deactivate selected templates"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} templates deactivated successfully.')
    deactivate_templates.short_description = "Deactivate selected templates"
    
    def mark_popular(self, request, queryset):
        """Mark selected templates as popular"""
        updated = queryset.update(is_popular=True)
        self.message_user(request, f'{updated} templates marked as popular.')
    mark_popular.short_description = "Mark as popular"
    
    def unmark_popular(self, request, queryset):
        """Unmark selected templates as popular"""
        updated = queryset.update(is_popular=False)
        self.message_user(request, f'{updated} templates unmarked as popular.')
    unmark_popular.short_description = "Unmark as popular"
    
    def bulk_update_templates(self, request, queryset):
        """Bulk update selected templates"""
        if 'apply' in request.POST:
            form = BulkBillingTemplateUpdateForm(request.POST)
            if form.is_valid():
                action = form.cleaned_data['action']
                templates = form.cleaned_data['templates']
                percentage = form.cleaned_data.get('percentage')
                new_sort_order = form.cleaned_data.get('new_sort_order')
                
                updated_count = 0
                
                for template in templates:
                    if action == 'activate':
                        template.is_active = True
                        template.save()
                        updated_count += 1
                    elif action == 'deactivate':
                        template.is_active = False
                        template.save()
                        updated_count += 1
                    elif action == 'mark_popular':
                        template.is_popular = True
                        template.save()
                        updated_count += 1
                    elif action == 'unmark_popular':
                        template.is_popular = False
                        template.save()
                        updated_count += 1
                    elif action == 'update_price' and percentage:
                        template.price = template.price * (1 + percentage / 100)
                        template.save()
                        updated_count += 1
                    elif action == 'update_sort_order' and new_sort_order:
                        template.sort_order = new_sort_order
                        template.save()
                        updated_count += 1
                
                self.message_user(request, f'{updated_count} templates updated successfully.')
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = BulkBillingTemplateUpdateForm(initial={'templates': queryset})
        
        return render(request, 'admin/billing_templates/billingtemplate/bulk_update.html', {
            'form': form,
            'templates': queryset,
            'title': 'Bulk Update Billing Templates'
        })
    bulk_update_templates.short_description = "Bulk update selected templates"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-update/', self.admin_site.admin_view(self.bulk_update_templates), name='billing_templates_billingtemplate_bulk_update'),
        ]
        return custom_urls + urls
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BillingTemplateUsage)
class BillingTemplateUsageAdmin(admin.ModelAdmin):
    list_display = ('template', 'user', 'generated_config', 'used_at')
    list_filter = ('used_at', 'template__duration_type')
    search_fields = ('template__name', 'user__email', 'user__username')
    raw_id_fields = ('template', 'user', 'generated_config')
    ordering = ('-used_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'template', 'user', 'generated_config'
        )


@admin.register(BillingTemplateCategoryAssignment)
class BillingTemplateCategoryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('template', 'category')
    list_filter = ('category',)
    search_fields = ('template__name', 'category__name')
    raw_id_fields = ('template', 'category')


# Custom admin dashboard for billing templates
class BillingTemplateDashboard:
    """Custom dashboard for billing template statistics"""
    
    def __init__(self, admin_site):
        self.admin_site = admin_site
    
    def get_urls(self):
        urls = [
            path('billing-dashboard/', self.admin_site.admin_view(self.dashboard_view), name='billing_templates_dashboard'),
        ]
        return urls
    
    def dashboard_view(self, request):
        """Dashboard view with billing template statistics"""
        
        # Template statistics
        total_templates = BillingTemplate.objects.count()
        active_templates = BillingTemplate.objects.filter(is_active=True).count()
        popular_templates = BillingTemplate.objects.filter(is_active=True, is_popular=True).count()
        
        # Usage statistics
        total_usage = BillingTemplateUsage.objects.count()
        recent_usage = BillingTemplateUsage.objects.filter(
            used_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Most used templates
        most_used = BillingTemplateUsage.objects.values('template__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Price statistics
        price_stats = BillingTemplate.objects.filter(is_active=True).aggregate(
            avg_price=models.Avg('price'),
            min_price=models.Min('price'),
            max_price=models.Max('price')
        )
        
        # Category statistics
        category_stats = BillingTemplateCategory.objects.annotate(
            template_count=Count('template_assignments', filter=models.Q(template_assignments__template__is_active=True))
        ).order_by('-template_count')
        
        context = {
            'title': 'Billing Templates Dashboard',
            'total_templates': total_templates,
            'active_templates': active_templates,
            'popular_templates': popular_templates,
            'total_usage': total_usage,
            'recent_usage': recent_usage,
            'most_used': most_used,
            'price_stats': price_stats,
            'category_stats': category_stats,
            'site_header': self.admin_site.site_header,
            'site_title': self.admin_site.site_title,
            'index_title': self.admin_site.index_title,
        }
        return render(request, 'admin/billing_templates/dashboard.html', context)


# Add dashboard to admin site
def add_billing_dashboard_to_admin(admin_site):
    """Add billing template dashboard to admin site"""
    dashboard = BillingTemplateDashboard(admin_site)
    original_get_urls = admin_site.get_urls
    admin_site.get_urls = lambda: dashboard.get_urls() + original_get_urls()

"""
Forms for Billing Templates
"""
from django import forms
from django.db import models
from .models import BillingTemplate, BillingTemplateCategory, BillingTemplateCategoryAssignment


class BillingTemplateForm(forms.ModelForm):
    """Form for creating and editing billing templates"""
    
    class Meta:
        model = BillingTemplate
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['mbps'].help_text = 'Download speed in Mbps (e.g., 5 for 5 Mbps)'
        self.fields['upload_mbps'].help_text = 'Upload speed in Mbps (optional, defaults to download speed)'
        self.fields['duration_value'].help_text = 'Duration value (e.g., 1 for 1 day, 7 for 7 days)'
        self.fields['price'].help_text = 'Price in the specified currency'
        self.fields['sort_order'].help_text = 'Lower numbers appear first'
    
    def clean(self):
        cleaned_data = super().clean()
        mbps = cleaned_data.get('mbps')
        upload_mbps = cleaned_data.get('upload_mbps')
        duration_value = cleaned_data.get('duration_value')
        
        # Validate bandwidth
        if mbps and mbps <= 0:
            self.add_error('mbps', 'Bandwidth must be greater than 0.')
        
        if upload_mbps and upload_mbps <= 0:
            self.add_error('upload_mbps', 'Upload bandwidth must be greater than 0.')
        
        if upload_mbps and mbps and upload_mbps > mbps:
            self.add_error('upload_mbps', 'Upload bandwidth cannot be greater than download bandwidth.')
        
        # Validate duration
        if duration_value and duration_value <= 0:
            self.add_error('duration_value', 'Duration value must be greater than 0.')
        
        return cleaned_data


class BillingTemplateCategoryForm(forms.ModelForm):
    """Form for creating and editing billing template categories"""
    
    class Meta:
        model = BillingTemplateCategory
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['color'].help_text = 'Color for category display (hex code)'
        self.fields['sort_order'].help_text = 'Lower numbers appear first'


class BulkBillingTemplateUpdateForm(forms.Form):
    """Form for bulk updating billing templates"""
    
    templates = forms.ModelMultipleChoiceField(
        queryset=BillingTemplate.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    action = forms.ChoiceField(
        choices=[
            ('activate', 'Activate'),
            ('deactivate', 'Deactivate'),
            ('mark_popular', 'Mark as Popular'),
            ('unmark_popular', 'Unmark as Popular'),
            ('update_price', 'Update Price by Percentage'),
            ('update_sort_order', 'Update Sort Order'),
        ],
        label="Action to perform"
    )
    percentage = forms.DecimalField(
        required=False,
        max_digits=5,
        decimal_places=2,
        help_text="Enter percentage (e.g., 10 for 10% increase, -5 for 5% decrease) for price update."
    )
    new_sort_order = forms.IntegerField(
        required=False,
        help_text="Enter new sort order for selected templates."
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        percentage = cleaned_data.get('percentage')
        new_sort_order = cleaned_data.get('new_sort_order')
        
        if action == 'update_price' and percentage is None:
            self.add_error('percentage', 'Percentage is required for price update.')
        if action == 'update_sort_order' and new_sort_order is None:
            self.add_error('new_sort_order', 'New sort order is required for sort order update.')
        
        return cleaned_data


class BillingTemplateSearchForm(forms.Form):
    """Form for searching billing templates"""
    
    search = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Search by name or description...'})
    )
    min_mbps = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Mbps'})
    )
    max_mbps = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Mbps'})
    )
    duration_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Durations')] + BillingTemplate.DURATION_CHOICES,
        widget=forms.Select()
    )
    max_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Price'})
    )
    popular_only = forms.BooleanField(
        required=False,
        label='Popular only'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        min_mbps = cleaned_data.get('min_mbps')
        max_mbps = cleaned_data.get('max_mbps')
        
        if min_mbps and max_mbps and min_mbps > max_mbps:
            self.add_error('min_mbps', 'Minimum Mbps cannot be greater than maximum Mbps.')
        
        return cleaned_data


class BillingTemplateCategoryAssignmentForm(forms.ModelForm):
    """Form for assigning templates to categories"""
    
    class Meta:
        model = BillingTemplateCategoryAssignment
        fields = ['template', 'category']
        widgets = {
            'template': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter to active templates and categories
        self.fields['template'].queryset = BillingTemplate.objects.filter(is_active=True)
        self.fields['category'].queryset = BillingTemplateCategory.objects.filter(is_active=True)

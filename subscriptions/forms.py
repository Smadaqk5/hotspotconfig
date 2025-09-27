from django import forms
from django.core.exceptions import ValidationError
import json
from .models import ProviderSubscriptionPlan


class SubscriptionPlanForm(forms.ModelForm):
    """Custom form for SubscriptionPlan admin"""
    
    features_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        help_text="Enter features as a JSON array, e.g., [\"Feature 1\", \"Feature 2\"]",
        required=False
    )
    
    class Meta:
        model = ProviderSubscriptionPlan
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'duration_days': forms.NumberInput(attrs={'min': '1', 'max': '365'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Convert features JSON to text for editing
            if self.instance.features:
                self.fields['features_text'].initial = json.dumps(self.instance.features, indent=2)
    
    def clean_features_text(self):
        features_text = self.cleaned_data.get('features_text')
        if not features_text:
            return []
        
        try:
            features = json.loads(features_text)
            if not isinstance(features, list):
                raise ValidationError("Features must be a JSON array")
            return features
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON format. Please enter a valid JSON array.")
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise ValidationError("Price cannot be negative")
        return price
    
    def clean_duration_days(self):
        duration = self.cleaned_data.get('duration_days')
        if duration and duration < 1:
            raise ValidationError("Duration must be at least 1 day")
        if duration and duration > 365:
            raise ValidationError("Duration cannot exceed 365 days")
        return duration
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.features = self.cleaned_data.get('features_text', [])
        if commit:
            instance.save()
        return instance


class BulkPlanUpdateForm(forms.Form):
    """Form for bulk updating subscription plans"""
    
    ACTION_CHOICES = [
        ('activate', 'Activate selected plans'),
        ('deactivate', 'Deactivate selected plans'),
        ('update_price', 'Update price by percentage'),
        ('update_duration', 'Update duration'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    percentage = forms.FloatField(
        required=False,
        help_text="Percentage change (e.g., 10 for 10% increase, -5 for 5% decrease)",
        widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    new_duration = forms.IntegerField(
        required=False,
        help_text="New duration in days",
        widget=forms.NumberInput(attrs={'min': '1', 'max': '365'})
    )
    plans = forms.ModelMultipleChoiceField(
        queryset=ProviderSubscriptionPlan.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        percentage = cleaned_data.get('percentage')
        new_duration = cleaned_data.get('new_duration')
        
        if action == 'update_price' and percentage is None:
            raise ValidationError("Percentage is required for price updates")
        
        if action == 'update_duration' and new_duration is None:
            raise ValidationError("New duration is required for duration updates")
        
        return cleaned_data

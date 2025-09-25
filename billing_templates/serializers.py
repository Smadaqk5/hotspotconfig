"""
Serializers for Billing Templates
"""
from rest_framework import serializers
from .models import BillingTemplate, BillingTemplateUsage, BillingTemplateCategory, BillingTemplateCategoryAssignment


class BillingTemplateSerializer(serializers.ModelSerializer):
    """Serializer for BillingTemplate model"""
    
    duration_display = serializers.ReadOnlyField()
    bandwidth_display = serializers.ReadOnlyField()
    price_display = serializers.ReadOnlyField()
    duration_seconds = serializers.ReadOnlyField()
    bandwidth_bytes = serializers.ReadOnlyField()
    upload_bandwidth_bytes = serializers.ReadOnlyField()
    
    class Meta:
        model = BillingTemplate
        fields = [
            'id', 'name', 'description', 'mbps', 'upload_mbps',
            'duration_type', 'duration_value', 'duration_display',
            'price', 'currency', 'price_display',
            'is_active', 'is_popular', 'sort_order',
            'bandwidth_display', 'duration_seconds', 'bandwidth_bytes', 'upload_bandwidth_bytes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BillingTemplateListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing billing templates"""
    
    duration_display = serializers.ReadOnlyField()
    bandwidth_display = serializers.ReadOnlyField()
    price_display = serializers.ReadOnlyField()
    
    class Meta:
        model = BillingTemplate
        fields = [
            'id', 'name', 'description', 'mbps', 'upload_mbps',
            'duration_type', 'duration_value', 'duration_display',
            'price', 'currency', 'price_display',
            'is_active', 'is_popular', 'sort_order',
            'bandwidth_display'
        ]


class BillingTemplateUsageSerializer(serializers.ModelSerializer):
    """Serializer for BillingTemplateUsage model"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = BillingTemplateUsage
        fields = [
            'id', 'template', 'template_name', 'user', 'user_email',
            'generated_config', 'used_at'
        ]
        read_only_fields = ['used_at']


class BillingTemplateCategorySerializer(serializers.ModelSerializer):
    """Serializer for BillingTemplateCategory model"""
    
    template_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BillingTemplateCategory
        fields = [
            'id', 'name', 'description', 'color', 'is_active',
            'sort_order', 'template_count'
        ]
    
    def get_template_count(self, obj):
        """Get count of active templates in this category"""
        return obj.template_assignments.filter(template__is_active=True).count()


class BillingTemplateCategoryAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for BillingTemplateCategoryAssignment model"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = BillingTemplateCategoryAssignment
        fields = [
            'id', 'template', 'template_name', 'category', 'category_name'
        ]


class BillingTemplateWithCategoriesSerializer(BillingTemplateSerializer):
    """Serializer for BillingTemplate with category information"""
    
    categories = serializers.SerializerMethodField()
    
    class Meta(BillingTemplateSerializer.Meta):
        fields = BillingTemplateSerializer.Meta.fields + ['categories']
    
    def get_categories(self, obj):
        """Get categories for this template"""
        assignments = obj.category_assignments.select_related('category').all()
        return BillingTemplateCategorySerializer(
            [assignment.category for assignment in assignments],
            many=True
        ).data


class BillingTemplateStatsSerializer(serializers.Serializer):
    """Serializer for billing template statistics"""
    
    total_templates = serializers.IntegerField()
    active_templates = serializers.IntegerField()
    popular_templates = serializers.IntegerField()
    total_usage = serializers.IntegerField()
    most_used_template = serializers.CharField()
    most_used_count = serializers.IntegerField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_range = serializers.DictField()


class BillingTemplateConfigDataSerializer(serializers.Serializer):
    """Serializer for billing template configuration data used in config generation"""
    
    template_id = serializers.IntegerField()
    template_name = serializers.CharField()
    mbps = serializers.IntegerField()
    upload_mbps = serializers.IntegerField(required=False, allow_null=True)
    duration_seconds = serializers.IntegerField()
    bandwidth_bytes = serializers.IntegerField()
    upload_bandwidth_bytes = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    
    def to_representation(self, instance):
        """Convert BillingTemplate instance to config data"""
        if isinstance(instance, BillingTemplate):
            return {
                'template_id': instance.id,
                'template_name': instance.name,
                'mbps': instance.mbps,
                'upload_mbps': instance.upload_mbps,
                'duration_seconds': instance.get_duration_seconds(),
                'bandwidth_bytes': instance.get_bandwidth_bytes(),
                'upload_bandwidth_bytes': instance.get_upload_bandwidth_bytes(),
                'price': instance.price,
                'currency': instance.currency,
            }
        return super().to_representation(instance)

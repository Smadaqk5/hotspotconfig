from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, SubscriptionUsage


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    days_remaining = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('user', 'start_date', 'created_at', 'updated_at')
    
    def get_days_remaining(self, obj):
        return obj.days_remaining()
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class SubscriptionUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionUsage
        fields = '__all__'

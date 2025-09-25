from rest_framework import serializers
from .models import MikroTikModel, VoucherType, BandwidthProfile, ConfigTemplate, GeneratedConfig


class MikroTikModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MikroTikModel
        fields = '__all__'


class VoucherTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherType
        fields = '__all__'


class BandwidthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandwidthProfile
        fields = '__all__'


class ConfigTemplateSerializer(serializers.ModelSerializer):
    mikrotik_model = MikroTikModelSerializer(read_only=True)
    
    class Meta:
        model = ConfigTemplate
        fields = '__all__'


class GeneratedConfigSerializer(serializers.ModelSerializer):
    template = ConfigTemplateSerializer(read_only=True)
    voucher_type = VoucherTypeSerializer(read_only=True)
    bandwidth_profile = BandwidthProfileSerializer(read_only=True)
    
    class Meta:
        model = GeneratedConfig
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class ConfigGenerationSerializer(serializers.Serializer):
    """Serializer for config generation request"""
    template_id = serializers.IntegerField()
    config_name = serializers.CharField(max_length=200)
    hotspot_name = serializers.CharField(max_length=100)
    hotspot_ip = serializers.IPAddressField()
    dns_servers = serializers.CharField(max_length=200)
    voucher_type_id = serializers.IntegerField()
    bandwidth_profile_id = serializers.IntegerField()
    billing_template_id = serializers.IntegerField(required=False, allow_null=True)
    max_users = serializers.IntegerField(default=50)
    voucher_length = serializers.IntegerField(default=8)
    voucher_prefix = serializers.CharField(max_length=10, required=False, allow_blank=True)

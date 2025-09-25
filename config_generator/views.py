from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from jinja2 import Template
from .models import MikroTikModel, VoucherType, BandwidthProfile, ConfigTemplate, GeneratedConfig
from .serializers import (
    MikroTikModelSerializer, VoucherTypeSerializer, BandwidthProfileSerializer,
    ConfigTemplateSerializer, GeneratedConfigSerializer, ConfigGenerationSerializer
)
from subscriptions.models import Subscription
import json


class MikroTikModelListView(generics.ListAPIView):
    """List all MikroTik models"""
    queryset = MikroTikModel.objects.filter(is_active=True)
    serializer_class = MikroTikModelSerializer
    permission_classes = [permissions.AllowAny]


class VoucherTypeListView(generics.ListAPIView):
    """List all voucher types"""
    queryset = VoucherType.objects.filter(is_active=True)
    serializer_class = VoucherTypeSerializer
    permission_classes = [permissions.AllowAny]


class BandwidthProfileListView(generics.ListAPIView):
    """List all bandwidth profiles"""
    queryset = BandwidthProfile.objects.filter(is_active=True)
    serializer_class = BandwidthProfileSerializer
    permission_classes = [permissions.AllowAny]


class ConfigTemplateListView(generics.ListAPIView):
    """List all config templates"""
    queryset = ConfigTemplate.objects.filter(is_active=True)
    serializer_class = ConfigTemplateSerializer
    permission_classes = [permissions.AllowAny]


class GeneratedConfigListView(generics.ListAPIView):
    """List user's generated configs"""
    serializer_class = GeneratedConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return GeneratedConfig.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_config(request):
    """Generate MikroTik configuration"""
    # Check if user has active subscription
    try:
        subscription = Subscription.objects.filter(
            user=request.user,
            is_active=True,
            status='active'
        ).latest('created_at')
        
        if subscription.is_expired():
            return Response(
                {'error': 'Subscription expired'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    except Subscription.DoesNotExist:
        return Response(
            {'error': 'No active subscription'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ConfigGenerationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Get template and related objects
    template = get_object_or_404(ConfigTemplate, id=data['template_id'], is_active=True)
    voucher_type = get_object_or_404(VoucherType, id=data['voucher_type_id'], is_active=True)
    bandwidth_profile = get_object_or_404(BandwidthProfile, id=data['bandwidth_profile_id'], is_active=True)
    
    # Prepare template context
    context = {
        'hotspot_name': data['hotspot_name'],
        'hotspot_ip': data['hotspot_ip'],
        'dns_servers': data['dns_servers'].split(','),
        'voucher_type': voucher_type,
        'bandwidth_profile': bandwidth_profile,
        'max_users': data['max_users'],
        'voucher_length': data['voucher_length'],
        'voucher_prefix': data.get('voucher_prefix', ''),
        'user': request.user,
    }
    
    # Generate config using Jinja2
    try:
        jinja_template = Template(template.template_content)
        config_content = jinja_template.render(**context)
    except Exception as e:
        return Response(
            {'error': f'Template rendering failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Save generated config
    generated_config = GeneratedConfig.objects.create(
        user=request.user,
        template=template,
        config_name=data['config_name'],
        config_content=config_content,
        hotspot_name=data['hotspot_name'],
        hotspot_ip=data['hotspot_ip'],
        dns_servers=data['dns_servers'],
        voucher_type=voucher_type,
        bandwidth_profile=bandwidth_profile,
        max_users=data['max_users'],
        voucher_length=data['voucher_length'],
        voucher_prefix=data.get('voucher_prefix', ''),
    )
    
    # Update subscription usage
    from subscriptions.models import SubscriptionUsage
    usage, created = SubscriptionUsage.objects.get_or_create(subscription=subscription)
    usage.configs_generated += 1
    usage.save()
    
    return Response({
        'config_id': generated_config.id,
        'config_content': config_content,
        'download_url': f'/api/config/download/{generated_config.id}/'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_config(request, config_id):
    """Download generated configuration file"""
    config = get_object_or_404(GeneratedConfig, id=config_id, user=request.user)
    
    response = HttpResponse(config.config_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{config.config_name}.rsc"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def config_preview(request, config_id):
    """Preview generated configuration"""
    config = get_object_or_404(GeneratedConfig, id=config_id, user=request.user)
    return Response({
        'config_name': config.config_name,
        'config_content': config.config_content,
        'created_at': config.created_at,
        'hotspot_name': config.hotspot_name,
        'hotspot_ip': config.hotspot_ip,
    })

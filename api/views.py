"""
API Views for MikroTik Hotspot Config Generator
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import timedelta

# Import models
from accounts.models import User, UserProfile
from subscriptions.models import SubscriptionPlan, Subscription, SubscriptionUsage
from payments.models import Payment, PaymentItem
from config_generator.models import MikroTikModel, VoucherType, BandwidthProfile, ConfigTemplate, GeneratedConfig
from billing_templates.models import BillingTemplate

# Import serializers
from accounts.serializers import UserSerializer, UserProfileSerializer
from subscriptions.serializers import SubscriptionPlanSerializer, SubscriptionSerializer
from payments.serializers import PaymentSerializer, PaymentItemSerializer
from config_generator.serializers import (
    MikroTikModelSerializer, VoucherTypeSerializer, BandwidthProfileSerializer,
    ConfigTemplateSerializer, GeneratedConfigSerializer, ConfigGenerationSerializer
)
from billing_templates.serializers import BillingTemplateListSerializer, BillingTemplateConfigDataSerializer


class APIStatsView(APIView):
    """API Statistics endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get API statistics"""
        user = request.user
        
        # User stats
        user_stats = {
            'total_users': User.objects.count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'active_users': User.objects.filter(is_active=True).count(),
        }
        
        # Subscription stats
        subscription_stats = {
            'total_plans': SubscriptionPlan.objects.count(),
            'active_plans': SubscriptionPlan.objects.filter(is_active=True).count(),
            'total_subscriptions': Subscription.objects.count(),
            'active_subscriptions': Subscription.objects.filter(is_active=True, status='active').count(),
        }
        
        # Payment stats
        payment_stats = {
            'total_payments': Payment.objects.count(),
            'completed_payments': Payment.objects.filter(status='completed').count(),
            'total_revenue': Payment.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0,
        }
        
        # Config stats
        config_stats = {
            'total_configs': GeneratedConfig.objects.count(),
            'user_configs': GeneratedConfig.objects.filter(user=user).count(),
            'total_models': MikroTikModel.objects.count(),
            'total_templates': ConfigTemplate.objects.count(),
        }
        
        return Response({
            'user_stats': user_stats,
            'subscription_stats': subscription_stats,
            'payment_stats': payment_stats,
            'config_stats': config_stats,
            'timestamp': timezone.now().isoformat(),
        })


class UserStatsView(APIView):
    """User-specific statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user-specific statistics"""
        user = request.user
        
        # User subscription info
        try:
            subscription = Subscription.objects.filter(
                user=user,
                is_active=True
            ).latest('created_at')
            subscription_data = SubscriptionSerializer(subscription).data
        except Subscription.DoesNotExist:
            subscription_data = None
        
        # User payment history
        payments = Payment.objects.filter(user=user).order_by('-created_at')[:10]
        payment_data = PaymentSerializer(payments, many=True).data
        
        # User generated configs
        configs = GeneratedConfig.objects.filter(user=user).order_by('-created_at')[:10]
        config_data = GeneratedConfigSerializer(configs, many=True).data
        
        # Usage statistics
        try:
            usage = SubscriptionUsage.objects.get(subscription__user=user)
            usage_data = {
                'configs_generated': usage.configs_generated,
                'last_used': usage.last_used,
            }
        except SubscriptionUsage.DoesNotExist:
            usage_data = {
                'configs_generated': 0,
                'last_used': None,
            }
        
        return Response({
            'user': UserSerializer(user).data,
            'subscription': subscription_data,
            'payments': payment_data,
            'configs': config_data,
            'usage': usage_data,
        })


class PublicPlansView(generics.ListAPIView):
    """Public subscription plans (no authentication required)"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class PublicModelsView(generics.ListAPIView):
    """Public MikroTik models (no authentication required)"""
    queryset = MikroTikModel.objects.filter(is_active=True)
    serializer_class = MikroTikModelSerializer
    permission_classes = [permissions.AllowAny]


class PublicVoucherTypesView(generics.ListAPIView):
    """Public voucher types (no authentication required)"""
    queryset = VoucherType.objects.filter(is_active=True)
    serializer_class = VoucherTypeSerializer
    permission_classes = [permissions.AllowAny]


class PublicBandwidthProfilesView(generics.ListAPIView):
    """Public bandwidth profiles (no authentication required)"""
    queryset = BandwidthProfile.objects.filter(is_active=True)
    serializer_class = BandwidthProfileSerializer
    permission_classes = [permissions.AllowAny]


class PublicTemplatesView(generics.ListAPIView):
    """Public config templates (no authentication required)"""
    queryset = ConfigTemplate.objects.filter(is_active=True)
    serializer_class = ConfigTemplateSerializer
    permission_classes = [permissions.AllowAny]


class PublicBillingTemplatesView(generics.ListAPIView):
    """Public billing templates (no authentication required)"""
    queryset = BillingTemplate.objects.filter(is_active=True).order_by('sort_order', 'price')
    serializer_class = BillingTemplateListSerializer
    permission_classes = [permissions.AllowAny]


class PopularBillingTemplatesView(generics.ListAPIView):
    """Popular billing templates (no authentication required)"""
    queryset = BillingTemplate.objects.filter(is_active=True, is_popular=True).order_by('sort_order', 'price')
    serializer_class = BillingTemplateListSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'database': 'connected',
            'authentication': 'active',
            'payments': 'ready',
            'config_generation': 'ready',
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_data(request):
    """Get comprehensive dashboard data for authenticated user"""
    user = request.user
    
    # Get user subscription
    try:
        subscription = Subscription.objects.filter(
            user=user,
            is_active=True
        ).latest('created_at')
        
        subscription_info = {
            'has_subscription': True,
            'plan_name': subscription.plan.name,
            'status': subscription.status,
            'is_active': subscription.status == 'active' and not subscription.is_expired(),
            'start_date': subscription.start_date,
            'end_date': subscription.end_date,
            'days_remaining': subscription.days_remaining(),
            'auto_renew': subscription.auto_renew,
        }
        
        # Get usage stats
        try:
            usage = SubscriptionUsage.objects.get(subscription=subscription)
            usage_info = {
                'configs_generated': usage.configs_generated,
                'last_used': usage.last_used,
            }
        except SubscriptionUsage.DoesNotExist:
            usage_info = {
                'configs_generated': 0,
                'last_used': None,
            }
            
    except Subscription.DoesNotExist:
        subscription_info = {
            'has_subscription': False,
            'message': 'No active subscription'
        }
        usage_info = {
            'configs_generated': 0,
            'last_used': None,
        }
    
    # Get recent payments
    recent_payments = Payment.objects.filter(user=user).order_by('-created_at')[:5]
    payments_data = []
    for payment in recent_payments:
        payments_data.append({
            'id': str(payment.id),
            'amount': float(payment.amount),
            'currency': payment.currency,
            'status': payment.status,
            'created_at': payment.created_at,
            'description': payment.description,
        })
    
    # Get recent generated configs
    recent_configs = GeneratedConfig.objects.filter(user=user).order_by('-created_at')[:5]
    configs_data = []
    for config in recent_configs:
        configs_data.append({
            'id': config.id,
            'config_name': config.config_name,
            'hotspot_name': config.hotspot_name,
            'created_at': config.created_at,
        })
    
    return Response({
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'company_name': user.company_name,
        },
        'subscription': subscription_info,
        'usage': usage_info,
        'recent_payments': payments_data,
        'recent_configs': configs_data,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_config_api(request):
    """Generate MikroTik configuration via API"""
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
    
    # Get billing template if provided
    billing_template = None
    if 'billing_template_id' in data and data['billing_template_id']:
        billing_template = get_object_or_404(BillingTemplate, id=data['billing_template_id'], is_active=True)
    
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
    
    # Add billing template context if provided
    if billing_template:
        context.update({
            'billing_template': billing_template,
            'bandwidth_mbps': billing_template.mbps,
            'upload_mbps': billing_template.upload_mbps or billing_template.mbps,
            'duration_seconds': billing_template.get_duration_seconds(),
            'bandwidth_bytes': billing_template.get_bandwidth_bytes(),
            'upload_bandwidth_bytes': billing_template.get_upload_bandwidth_bytes(),
            'duration_type': billing_template.duration_type,
            'duration_value': billing_template.duration_value,
        })
    
    # Generate config using Jinja2
    try:
        from jinja2 import Template
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
        billing_template=billing_template,
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
        # Add billing template data
        bandwidth_mbps=billing_template.mbps if billing_template else None,
        upload_mbps=billing_template.upload_mbps if billing_template else None,
        duration_seconds=billing_template.get_duration_seconds() if billing_template else None,
    )
    
    # Track billing template usage if used
    if billing_template:
        from billing_templates.models import BillingTemplateUsage
        BillingTemplateUsage.objects.create(
            template=billing_template,
            user=request.user,
            generated_config=generated_config
        )
    
    # Update subscription usage
    usage, created = SubscriptionUsage.objects.get_or_create(subscription=subscription)
    usage.configs_generated += 1
    usage.save()
    
    return Response({
        'config_id': generated_config.id,
        'config_content': config_content,
        'download_url': f'/api/config/download/{generated_config.id}/',
        'billing_template_used': billing_template.name if billing_template else None,
        'message': 'Configuration generated successfully'
    }, status=status.HTTP_201_CREATED)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from subscriptions.models import ProviderSubscription, SubscriptionUsage
from payments.models import Payment
from config_generator.models import GeneratedConfig


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the user"""
    user = request.user
    
    # Get current subscription
    try:
        subscription = ProviderSubscription.objects.filter(
            user=user,
            is_active=True
        ).latest('created_at')
        
        subscription_data = {
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
            usage = ProviderSubscriptionUsage.objects.get(subscription=subscription)
            usage_data = {
                'configs_generated': usage.configs_generated,
                'last_used': usage.last_used,
            }
        except ProviderSubscriptionUsage.DoesNotExist:
            usage_data = {
                'configs_generated': 0,
                'last_used': None,
            }
            
    except ProviderSubscription.DoesNotExist:
        subscription_data = None
        usage_data = None
    
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
        'subscription': subscription_data,
        'usage': usage_data,
        'recent_payments': payments_data,
        'recent_configs': configs_data,
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'company_name': user.company_name,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    """Get detailed subscription status"""
    try:
        subscription = ProviderSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).latest('created_at')
        
        return Response({
            'has_subscription': True,
            'subscription': {
                'id': subscription.id,
                'plan_name': subscription.plan.name,
                'plan_description': subscription.plan.description,
                'status': subscription.status,
                'is_active': subscription.status == 'active' and not subscription.is_expired(),
                'start_date': subscription.start_date,
                'end_date': subscription.end_date,
                'days_remaining': subscription.days_remaining(),
                'auto_renew': subscription.auto_renew,
                'created_at': subscription.created_at,
            }
        })
    except ProviderSubscription.DoesNotExist:
        return Response({
            'has_subscription': False,
            'message': 'No active subscription found'
        })


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    return render(request, 'dashboard.html', {
        'user': request.user,
        'page_title': 'Dashboard'
    })


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'profile.html', {
        'user': request.user,
        'page_title': 'Profile'
    })

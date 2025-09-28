"""
Subscription management views for providers
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
import json

from accounts.models import Provider
from .models import ProviderSubscription, ProviderSubscriptionPlan
from .pesapal_integration import SubscriptionPaymentService

def is_provider(user):
    """Check if user is a provider"""
    return user.is_authenticated and (user.user_type == 'provider' or user.is_superuser)

@login_required
@user_passes_test(is_provider)
def subscription_plans(request):
    """View available subscription plans"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get available plans
    plans = ProviderSubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    # Get current subscription
    current_subscription = ProviderSubscription.objects.filter(
        provider=provider,
        status__in=['active', 'pending']
    ).first()
    
    context = {
        'page_title': 'Subscription Plans',
        'plans': plans,
        'current_subscription': current_subscription,
        'provider': provider,
    }
    
    return render(request, 'subscriptions/plans.html', context)

@login_required
@user_passes_test(is_provider)
def subscribe_to_plan(request, plan_id):
    """Subscribe to a specific plan"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    plan = get_object_or_404(ProviderSubscriptionPlan, id=plan_id, is_active=True)
    
    # Check if provider already has an active subscription
    active_subscription = ProviderSubscription.objects.filter(
        provider=provider,
        status='active'
    ).first()
    
    if active_subscription:
        messages.warning(request, 'You already have an active subscription.')
        return redirect('subscriptions:my_subscription')
    
    # Check if provider has a pending subscription
    pending_subscription = ProviderSubscription.objects.filter(
        provider=provider,
        status='pending'
    ).first()
    
    if pending_subscription:
        messages.info(request, 'You have a pending subscription. Please complete the payment.')
        return redirect('subscriptions:my_subscription')
    
    # Initiate payment
    payment_service = SubscriptionPaymentService()
    redirect_url, subscription = payment_service.initiate_subscription_payment(provider, plan)
    
    if redirect_url:
        # Store subscription ID in session for callback handling
        request.session['pending_subscription_id'] = subscription.id
        return redirect(redirect_url)
    else:
        messages.error(request, f'Failed to initiate payment: {subscription}')
        return redirect('subscriptions:plans')

@login_required
@user_passes_test(is_provider)
def my_subscription(request):
    """View current subscription details"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get current subscription
    subscription = ProviderSubscription.objects.filter(
        provider=provider
    ).order_by('-created_at').first()
    
    # Get subscription history
    subscription_history = ProviderSubscription.objects.filter(
        provider=provider
    ).order_by('-created_at')[:10]
    
    context = {
        'page_title': 'My Subscription',
        'subscription': subscription,
        'subscription_history': subscription_history,
        'provider': provider,
    }
    
    return render(request, 'subscriptions/my_subscription.html', context)

@login_required
@user_passes_test(is_provider)
def subscription_payment_callback(request):
    """Handle payment callback from Pesapal"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        return JsonResponse({'error': 'Provider profile not found'}, status=400)
    
    # Get parameters from request
    order_tracking_id = request.GET.get('OrderTrackingId')
    payment_method = request.GET.get('PaymentMethod')
    payment_account = request.GET.get('PaymentAccount')
    
    if not order_tracking_id:
        return JsonResponse({'error': 'Order tracking ID required'}, status=400)
    
    # Handle payment callback
    payment_service = SubscriptionPaymentService()
    success, message = payment_service.handle_payment_callback(
        order_tracking_id, payment_method, payment_account
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('subscriptions:my_subscription')

@login_required
@user_passes_test(is_provider)
def check_subscription_status(request, subscription_id):
    """Check subscription status with Pesapal"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        return JsonResponse({'error': 'Provider profile not found'}, status=400)
    
    subscription = get_object_or_404(ProviderSubscription, id=subscription_id, provider=provider)
    
    # Check status with Pesapal
    payment_service = SubscriptionPaymentService()
    success, status_data = payment_service.check_subscription_status(subscription)
    
    if success:
        return JsonResponse({
            'success': True,
            'status': status_data.get('payment_status'),
            'message': status_data.get('message', 'Status checked successfully')
        })
    else:
        return JsonResponse({
            'success': False,
            'error': status_data
        }, status=400)

@login_required
@user_passes_test(is_provider)
def cancel_subscription(request, subscription_id):
    """Cancel subscription"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    subscription = get_object_or_404(ProviderSubscription, id=subscription_id, provider=provider)
    
    if subscription.status not in ['active', 'pending']:
        messages.warning(request, 'Subscription cannot be cancelled.')
        return redirect('subscriptions:my_subscription')
    
    # Cancel subscription
    subscription.status = 'cancelled'
    subscription.cancelled_at = timezone.now()
    subscription.save()
    
    # Update provider subscription status
    provider.subscription_status = 'inactive'
    provider.save()
    
    messages.success(request, 'Subscription cancelled successfully.')
    return redirect('subscriptions:my_subscription')

@login_required
@user_passes_test(is_provider)
def subscription_usage(request):
    """View subscription usage statistics"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get current subscription
    subscription = ProviderSubscription.objects.filter(
        provider=provider,
        status='active'
    ).first()
    
    if not subscription:
        messages.warning(request, 'No active subscription found.')
        return redirect('subscriptions:plans')
    
    # Get usage statistics
    from tickets.models import Ticket, TicketSale
    from payments.models import Payment
    
    # Ticket statistics
    total_tickets = Ticket.objects.filter(provider=provider).count()
    active_tickets = Ticket.objects.filter(provider=provider, status='active').count()
    
    # Revenue statistics
    total_revenue = Payment.objects.filter(
        provider=provider,
        status='completed'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Monthly usage
    from datetime import datetime, timedelta
    current_month = timezone.now().replace(day=1)
    monthly_tickets = Ticket.objects.filter(
        provider=provider,
        created_at__gte=current_month
    ).count()
    
    monthly_revenue = Payment.objects.filter(
        provider=provider,
        status='completed',
        created_at__gte=current_month
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    context = {
        'page_title': 'Subscription Usage',
        'subscription': subscription,
        'total_tickets': total_tickets,
        'active_tickets': active_tickets,
        'total_revenue': total_revenue,
        'monthly_tickets': monthly_tickets,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'subscriptions/usage.html', context)

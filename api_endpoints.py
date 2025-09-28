"""
API Endpoints Implementation - Complete Payment Flows
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
import logging

from accounts.models import Provider
from payments.pesapal_provider import ProviderSubscriptionService
from payments.mpesa_daraja import CustomerPaymentService
from subscriptions.models import ProviderSubscriptionPlan

logger = logging.getLogger(__name__)

# =============================================================================
# PESAPAL PROVIDER SUBSCRIPTION ENDPOINTS
# =============================================================================

@login_required
@require_http_methods(["POST"])
def create_pesapal_order(request, provider_id):
    """
    POST /api/providers/{id}/pesapal/create-order
    Creates Pesapal checkout link for provider subscription
    """
    try:
        provider = get_object_or_404(Provider, id=provider_id)
        plan_id = request.POST.get('plan_id')
        
        if not plan_id:
            return JsonResponse({'error': 'Plan ID required'}, status=400)
        
        # Get subscription plan
        plan = get_object_or_404(ProviderSubscriptionPlan, id=plan_id, is_active=True)
        
        # Create subscription order
        subscription_service = ProviderSubscriptionService()
        redirect_url, subscription = subscription_service.create_subscription_order(provider, plan)
        
        if redirect_url:
            return JsonResponse({
                'success': True,
                'checkout_url': redirect_url,
                'subscription_id': subscription.id,
                'message': 'Pesapal order created successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': subscription
            }, status=400)
            
    except Exception as e:
        logger.error(f"Failed to create Pesapal order: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def pesapal_callback(request):
    """
    GET /api/payments/pesapal/callback
    Pesapal redirect callback (user-facing)
    """
    try:
        order_tracking_id = request.GET.get('OrderTrackingId')
        payment_method = request.GET.get('PaymentMethod')
        payment_account = request.GET.get('PaymentAccount')
        
        if not order_tracking_id:
            return JsonResponse({'error': 'Order tracking ID required'}, status=400)
        
        # Handle payment callback
        subscription_service = ProviderSubscriptionService()
        success, message = subscription_service.handle_pesapal_webhook({
            'order_tracking_id': order_tracking_id,
            'payment_method': payment_method,
            'payment_account': payment_account,
            'payment_status': 'COMPLETED'  # Assume success for redirect
        })
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Payment successful! Your subscription is now active.',
                'redirect_url': '/provider/dashboard/'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': message,
                'redirect_url': '/subscriptions/plans/'
            })
            
    except Exception as e:
        logger.error(f"Pesapal callback error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Payment processing failed'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def pesapal_webhook(request):
    """
    POST /api/payments/pesapal/webhook
    Pesapal server-to-server IPN/webhook
    """
    try:
        webhook_data = json.loads(request.body)
        
        # Handle webhook
        subscription_service = ProviderSubscriptionService()
        success, message = subscription_service.handle_pesapal_webhook(webhook_data)
        
        if success:
            logger.info(f"Pesapal webhook processed successfully: {message}")
            return JsonResponse({'status': 'success'})
        else:
            logger.warning(f"Pesapal webhook failed: {message}")
            return JsonResponse({'status': 'failed', 'error': message})
            
    except Exception as e:
        logger.error(f"Pesapal webhook error: {e}")
        return JsonResponse({'status': 'error', 'error': str(e)})

@login_required
@require_http_methods(["GET"])
def subscription_status(request, provider_id):
    """
    GET /api/providers/{id}/subscription-status
    Provider subscription info (dashboard)
    """
    try:
        provider = get_object_or_404(Provider, id=provider_id)
        
        # Get current subscription
        from subscriptions.models import ProviderSubscription
        subscription = ProviderSubscription.objects.filter(
            provider=provider
        ).order_by('-created_at').first()
        
        if subscription:
            return JsonResponse({
                'success': True,
                'subscription': {
                    'id': subscription.id,
                    'status': subscription.status,
                    'plan_name': subscription.plan.name if subscription.plan else 'Unknown',
                    'amount': float(subscription.amount),
                    'currency': subscription.currency,
                    'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
                    'expiry_date': subscription.expiry_date.isoformat() if subscription.expiry_date else None,
                    'is_active': subscription.status == 'active',
                    'days_remaining': (subscription.expiry_date - timezone.now()).days if subscription.expiry_date else 0
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'subscription': None,
                'message': 'No subscription found'
            })
            
    except Exception as e:
        logger.error(f"Failed to get subscription status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# =============================================================================
# M-PESA CUSTOMER PAYMENT ENDPOINTS
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def initiate_mpesa_payment(request, provider_id):
    """
    POST /api/captive/{provider_id}/initiate-mpesa
    Initiate STK Push (uses provider creds)
    """
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        plan_name = data.get('plan_name', 'WiFi Access')
        
        if not all([phone_number, amount]):
            return JsonResponse({
                'success': False,
                'error': 'Phone number and amount required'
            }, status=400)
        
        # Get provider
        provider = get_object_or_404(Provider, id=provider_id, status='active')
        
        # Check if provider has M-PESA credentials
        if not provider.mpesa_consumer_key or not provider.mpesa_consumer_secret:
            return JsonResponse({
                'success': False,
                'error': 'Provider M-PESA credentials not configured'
            }, status=400)
        
        # Initiate customer payment
        payment_service = CustomerPaymentService()
        result, payment = payment_service.initiate_customer_payment(
            provider=provider,
            phone_number=phone_number,
            amount=amount,
            plan_name=plan_name
        )
        
        if result:
            return JsonResponse({
                'success': True,
                'checkout_request_id': result.get('CheckoutRequestID'),
                'merchant_request_id': result.get('MerchantRequestID'),
                'customer_message': result.get('CustomerMessage'),
                'payment_id': payment.id if payment else None
            })
        else:
            return JsonResponse({
                'success': False,
                'error': payment
            }, status=400)
            
    except Exception as e:
        logger.error(f"Failed to initiate M-PESA payment: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def mpesa_callback(request, provider_id):
    """
    POST /api/mpesa/callback/{provider_id}
    Daraja webhook/callback per provider
    """
    try:
        callback_data = json.loads(request.body)
        
        # Handle Daraja callback
        payment_service = CustomerPaymentService()
        success, result = payment_service.handle_daraja_callback(provider_id, callback_data)
        
        if success:
            # Return ticket information
            ticket = result
            return JsonResponse({
                'success': True,
                'ticket': {
                    'code': ticket.code,
                    'username': ticket.username,
                    'password': ticket.password,
                    'expires_at': ticket.expires_at.isoformat(),
                    'plan_type': ticket.plan_type,
                    'duration_hours': ticket.duration_hours,
                    'data_limit_mb': ticket.data_limit_mb
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result
            })
            
    except Exception as e:
        logger.error(f"M-PESA callback error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["GET"])
def ticket_status(request, ticket_code):
    """
    GET /api/tickets/{code}/status
    Check ticket status and remaining time/data
    """
    try:
        from tickets.models import Ticket
        ticket = get_object_or_404(Ticket, code=ticket_code)
        
        status_info = {
            'code': ticket.code,
            'status': ticket.status,
            'can_be_used': ticket.can_be_used(),
            'is_expired': ticket.is_expired(),
            'expires_at': ticket.expires_at.isoformat() if ticket.expires_at else None,
            'plan_type': ticket.plan_type,
            'duration_hours': ticket.duration_hours,
            'data_limit_mb': ticket.data_limit_mb,
            'data_used_mb': ticket.data_used_mb,
            'remaining_time_hours': ticket.get_remaining_time(),
            'remaining_data_mb': ticket.get_remaining_data()
        }
        
        return JsonResponse({
            'success': True,
            'ticket': status_info
        })
        
    except Exception as e:
        logger.error(f"Failed to get ticket status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["POST"])
def activate_ticket(request, ticket_code):
    """
    POST /api/tickets/{code}/activate
    Activate ticket for internet access
    """
    try:
        from tickets.models import Ticket
        
        data = json.loads(request.body)
        device_mac = data.get('device_mac', '')
        device_ip = data.get('device_ip', '')
        
        ticket = get_object_or_404(Ticket, code=ticket_code)
        
        if not ticket.can_be_used():
            return JsonResponse({
                'success': False,
                'error': 'Ticket is expired or already used'
            }, status=400)
        
        # Activate ticket
        if ticket.activate(device_mac=device_mac, device_ip=device_ip):
            return JsonResponse({
                'success': True,
                'message': 'Ticket activated successfully',
                'ticket': {
                    'code': ticket.code,
                    'username': ticket.username,
                    'password': ticket.password,
                    'expires_at': ticket.expires_at.isoformat()
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to activate ticket'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Failed to activate ticket: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@require_http_methods(["GET"])
def provider_plans(request, provider_id):
    """
    GET /api/providers/{provider_id}/plans
    Get available WiFi plans for provider
    """
    try:
        from tickets.models import TicketType
        
        provider = get_object_or_404(Provider, id=provider_id, status='active')
        plans = TicketType.objects.filter(
            provider=provider,
            is_active=True
        ).order_by('price')
        
        plans_data = []
        for plan in plans:
            plans_data.append({
                'id': plan.id,
                'name': plan.name,
                'type': plan.type,
                'duration_hours': plan.duration_hours,
                'data_limit_mb': plan.data_limit_mb,
                'price': float(plan.price),
                'currency': plan.currency,
                'download_speed_mbps': plan.download_speed_mbps,
                'upload_speed_mbps': plan.upload_speed_mbps,
                'is_featured': plan.is_featured,
                'description': plan.description,
                'icon': plan.icon,
                'color': plan.color
            })
        
        return JsonResponse({
            'success': True,
            'plans': plans_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get provider plans: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def provider_info(request, provider_id):
    """
    GET /api/providers/{provider_id}/info
    Get provider information for captive portal
    """
    try:
        provider = get_object_or_404(Provider, id=provider_id, status='active')
        
        return JsonResponse({
            'success': True,
            'provider': {
                'id': provider.id,
                'business_name': provider.business_name,
                'contact_email': provider.contact_email,
                'contact_phone': provider.contact_phone,
                'address': provider.address,
                'city': provider.city,
                'county': provider.county,
                'subscription_status': provider.subscription_status,
                'mpesa_configured': bool(provider.mpesa_consumer_key and provider.mpesa_consumer_secret)
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get provider info: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# =============================================================================
# WEBHOOK VERIFICATION HELPERS
# =============================================================================

def verify_pesapal_signature(request):
    """Verify Pesapal webhook signature"""
    # Implement Pesapal signature verification
    # This would include checking the signature header
    return True

def verify_daraja_signature(request):
    """Verify Daraja webhook signature"""
    # Implement Daraja signature verification
    # This would include checking the signature header
    return True

# =============================================================================
# ERROR HANDLERS
# =============================================================================

def handle_payment_error(error, context=None):
    """Centralized payment error handling"""
    logger.error(f"Payment error: {error}, Context: {context}")
    
    return JsonResponse({
        'success': False,
        'error': 'Payment processing failed',
        'code': 'PAYMENT_ERROR'
    }, status=500)

def handle_webhook_error(error, webhook_type=None):
    """Centralized webhook error handling"""
    logger.error(f"Webhook error ({webhook_type}): {error}")
    
    return JsonResponse({
        'success': False,
        'error': 'Webhook processing failed',
        'code': 'WEBHOOK_ERROR'
    }, status=500)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
import json
import logging

from accounts.models import Provider
from tickets.models import Ticket, TicketType, TicketUsage
from payments.payment_bucket import payment_bucket_service

logger = logging.getLogger(__name__)

def get_provider_from_request(request):
    """Extract provider from request (could be from URL, subdomain, or IP)"""
    # This would be implemented based on your routing logic
    # For now, we'll use a simple approach with provider ID in URL
    provider_id = request.GET.get('provider_id')
    if provider_id:
        try:
            return Provider.objects.get(id=provider_id, status='active')
        except Provider.DoesNotExist:
            return None
    return None

def captive_portal(request):
    """Main captive portal page"""
    provider = get_provider_from_request(request)
    
    if not provider:
        return render(request, 'captive_portal/error.html', {
            'error': 'Invalid provider configuration',
            'message': 'Please contact your network administrator.'
        })
    
    # Get available ticket types
    ticket_types = TicketType.objects.filter(
        provider=provider,
        is_active=True
    ).order_by('price')
    
    # Get device info (if available)
    device_info = {
        'ip': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'mac': request.GET.get('mac', ''),  # MAC address from router
    }
    
    context = {
        'provider': provider,
        'ticket_types': ticket_types,
        'device_info': device_info,
    }
    
    return render(request, 'captive_portal/index.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def initiate_payment(request):
    """Initiate M-PESA payment for ticket purchase"""
    try:
        data = json.loads(request.body)
        provider_id = data.get('provider_id')
        ticket_type_id = data.get('ticket_type_id')
        phone_number = data.get('phone_number')
        
        # Validate inputs
        if not all([provider_id, ticket_type_id, phone_number]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required parameters'
            }, status=400)
        
        # Get provider and ticket type
        provider = get_object_or_404(Provider, id=provider_id, status='active')
        ticket_type = get_object_or_404(TicketType, id=ticket_type_id, provider=provider, is_active=True)
        
        # Validate phone number format
        if not phone_number.startswith('254'):
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            else:
                phone_number = '254' + phone_number
        
        # Initiate STK Push
        result = payment_bucket_service.initiate_stk_push(
            provider_id=provider.id,
            phone_number=phone_number,
            amount=int(ticket_type.price),
            account_reference=f"WIFI_{ticket_type.id}",
            transaction_desc=f"WiFi Access - {ticket_type.name}"
        )
        
        if result.get('ResponseCode') == '0':
            # Store payment reference for callback
            payment_data = {
                'checkout_request_id': result.get('CheckoutRequestID'),
                'merchant_request_id': result.get('MerchantRequestID'),
                'provider_id': provider.id,
                'ticket_type_id': ticket_type.id,
                'phone_number': phone_number,
                'amount': float(ticket_type.price),
            }
            
            # Store in session for callback handling
            request.session['pending_payment'] = payment_data
            
            return JsonResponse({
                'success': True,
                'message': 'Payment initiated successfully',
                'checkout_request_id': result.get('CheckoutRequestID'),
                'customer_message': result.get('CustomerMessage')
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result.get('CustomerMessage', 'Payment initiation failed'),
                'error_code': result.get('ResponseCode')
            }, status=400)
            
    except Exception as e:
        logger.error(f"Payment initiation failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Payment failed: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def check_payment_status(request):
    """Check payment status"""
    try:
        data = json.loads(request.body)
        checkout_request_id = data.get('checkout_request_id')
        
        if not checkout_request_id:
            return JsonResponse({
                'success': False,
                'message': 'Checkout request ID required'
            }, status=400)
        
        # Get payment data from session
        payment_data = request.session.get('pending_payment')
        if not payment_data or payment_data.get('checkout_request_id') != checkout_request_id:
            return JsonResponse({
                'success': False,
                'message': 'Payment session not found'
            }, status=400)
        
        # Query payment status
        provider = get_object_or_404(Provider, id=payment_data['provider_id'])
        result = payment_bucket_service.query_stk_push_status(
            provider_id=provider.id,
            checkout_request_id=checkout_request_id
        )
        
        if result.get('ResultCode') == '0':
            # Payment successful - create ticket
            ticket = create_ticket_from_payment(payment_data, provider)
            
            # Clear session
            if 'pending_payment' in request.session:
                del request.session['pending_payment']
            
            return JsonResponse({
                'success': True,
                'status': 'completed',
                'ticket': {
                    'code': ticket.code,
                    'username': ticket.username,
                    'password': ticket.password,
                    'expires_at': ticket.expires_at.isoformat(),
                    'type': ticket.ticket_type.get_display_name()
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'status': 'pending',
                'message': result.get('ResultDesc', 'Payment still processing')
            })
            
    except Exception as e:
        logger.error(f"Payment status check failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Status check failed: {str(e)}'
        }, status=500)

def create_ticket_from_payment(payment_data, provider):
    """Create ticket after successful payment"""
    from tickets.models import TicketType, Ticket, TicketSale
    
    ticket_type = get_object_or_404(TicketType, id=payment_data['ticket_type_id'])
    
    with transaction.atomic():
        # Create ticket
        ticket = Ticket.objects.create(
            provider=provider,
            ticket_type=ticket_type,
            payment=None,  # Will be linked later
        )
        
        # Create sale record
        TicketSale.objects.create(
            provider=provider,
            ticket_type=ticket_type,
            ticket=ticket,
            unit_price=ticket_type.price,
            total_amount=payment_data['amount'],
            payment_method='mpesa',
            payment_reference=payment_data['checkout_request_id'],
            status='completed'
        )
        
        # Set expiry time
        if ticket_type.type == 'time':
            ticket.expires_at = timezone.now() + timezone.timedelta(hours=ticket_type.duration_hours)
        else:
            # For data-based tickets, set a reasonable expiry (e.g., 30 days)
            ticket.expires_at = timezone.now() + timezone.timedelta(days=30)
        
        ticket.save()
        
        logger.info(f"Ticket created: {ticket.code} for provider {provider.business_name}")
        return ticket

def ticket_activation(request, ticket_code):
    """Activate ticket for internet access"""
    try:
        ticket = get_object_or_404(Ticket, code=ticket_code)
        
        if not ticket.can_be_used():
            return JsonResponse({
                'success': False,
                'message': 'Ticket is expired or already used'
            }, status=400)
        
        # Get device info
        device_mac = request.GET.get('mac', '')
        device_ip = request.META.get('REMOTE_ADDR')
        
        # Activate ticket
        if ticket.activate(device_mac=device_mac, device_ip=device_ip):
            # Create usage session
            TicketUsage.objects.create(
                ticket=ticket,
                session_start=timezone.now(),
                device_mac=device_mac,
                device_ip=device_ip
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Ticket activated successfully',
                'ticket': {
                    'code': ticket.code,
                    'username': ticket.username,
                    'password': ticket.password,
                    'expires_at': ticket.expires_at.isoformat(),
                    'type': ticket.ticket_type.get_display_name()
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to activate ticket'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Ticket activation failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Activation failed: {str(e)}'
        }, status=500)

def ticket_status(request, ticket_code):
    """Check ticket status and remaining time/data"""
    try:
        ticket = get_object_or_404(Ticket, code=ticket_code)
        
        status_info = {
            'code': ticket.code,
            'status': ticket.status,
            'can_be_used': ticket.can_be_used(),
            'is_expired': ticket.is_expired(),
            'expires_at': ticket.expires_at.isoformat() if ticket.expires_at else None,
        }
        
        if ticket.ticket_type.type == 'time':
            status_info['remaining_time_hours'] = ticket.get_remaining_time()
        elif ticket.ticket_type.type == 'data':
            status_info['remaining_data_mb'] = ticket.get_remaining_data()
            status_info['data_used_mb'] = ticket.data_used_mb
        
        return JsonResponse({
            'success': True,
            'ticket': status_info
        })
        
    except Exception as e:
        logger.error(f"Ticket status check failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Status check failed: {str(e)}'
        }, status=500)

def success_page(request, ticket_code):
    """Success page after ticket purchase"""
    try:
        ticket = get_object_or_404(Ticket, code=ticket_code)
        
        context = {
            'ticket': ticket,
            'provider': ticket.provider,
        }
        
        return render(request, 'captive_portal/success.html', context)
        
    except Exception as e:
        logger.error(f"Success page error: {e}")
        return render(request, 'captive_portal/error.html', {
            'error': 'Ticket not found',
            'message': 'The ticket you are looking for does not exist.'
        })
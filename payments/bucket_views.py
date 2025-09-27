"""
Payment Bucket API Views
Handles M-PESA payments using provider-specific credentials
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Provider
from accounts.encryption import encrypt_mpesa_credential, decrypt_mpesa_credential
from payments.payment_bucket import PaymentBucketService, process_payment_callback
from tickets.models import Ticket, TicketSale
import uuid

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """Initiate STK Push payment using provider's credentials"""
    try:
        data = request.data
        provider_id = data.get('provider_id')
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        ticket_id = data.get('ticket_id')
        account_reference = data.get('account_reference', f"WIFI_{ticket_id}")
        transaction_desc = data.get('transaction_desc', 'WiFi Voucher Purchase')
        
        # Validate required fields
        if not all([provider_id, phone_number, amount, ticket_id]):
            return Response({
                'success': False,
                'message': 'Missing required fields: provider_id, phone_number, amount, ticket_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get provider
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Provider not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if provider has M-PESA credentials
        if not provider.mpesa_consumer_key or not provider.mpesa_consumer_secret:
            return Response({
                'success': False,
                'message': 'Provider M-PESA credentials not configured'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get ticket
        try:
            ticket = Ticket.objects.get(id=ticket_id, provider=provider)
        except Ticket.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Ticket not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create ticket sale record
        ticket_sale = TicketSale.objects.create(
            provider=provider,
            ticket=ticket,
            customer_phone=phone_number,
            quantity=1,
            unit_price=float(amount),
            total_amount=float(amount),
            currency='KES',
            payment_method='mpesa',
            status='pending'
        )
        
        # Initialize payment bucket service
        payment_service = PaymentBucketService(provider_id)
        
        # Initiate STK Push
        result = payment_service.initiate_stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            transaction_desc=transaction_desc
        )
        
        if result['success']:
            # Update ticket sale with checkout request ID
            ticket_sale.payment_reference = result['checkout_request_id']
            ticket_sale.save()
            
            return Response({
                'success': True,
                'message': 'STK Push initiated successfully',
                'checkout_request_id': result['checkout_request_id'],
                'merchant_request_id': result['merchant_request_id'],
                'ticket_sale_id': ticket_sale.id
            })
        else:
            # Update ticket sale status to failed
            ticket_sale.status = 'failed'
            ticket_sale.save()
            
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error initiating payment: {e}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_payment_status(request):
    """Query STK Push payment status"""
    try:
        data = request.data
        provider_id = data.get('provider_id')
        checkout_request_id = data.get('checkout_request_id')
        
        if not all([provider_id, checkout_request_id]):
            return Response({
                'success': False,
                'message': 'Missing required fields: provider_id, checkout_request_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize payment bucket service
        payment_service = PaymentBucketService(provider_id)
        
        # Query payment status
        result = payment_service.query_stk_push_status(checkout_request_id)
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error querying payment status: {e}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_provider_credentials(request):
    """Test provider's M-PESA credentials"""
    try:
        data = request.data
        provider_id = data.get('provider_id')
        
        if not provider_id:
            return Response({
                'success': False,
                'message': 'Provider ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get provider
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Provider not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if provider has M-PESA credentials
        if not provider.mpesa_consumer_key or not provider.mpesa_consumer_secret:
            return Response({
                'success': False,
                'message': 'M-PESA credentials not configured'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Test credentials
        payment_service = PaymentBucketService(provider_id)
        is_valid = payment_service.test_credentials()
        
        return Response({
            'success': is_valid,
            'message': 'Credentials are valid' if is_valid else 'Credentials are invalid',
            'provider_id': provider_id,
            'verified': provider.mpesa_credentials_verified,
            'last_test': provider.mpesa_last_test,
            'test_status': provider.mpesa_test_status
        })
        
    except Exception as e:
        logger.error(f"Error testing credentials: {e}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
def mpesa_callback(request, provider_id):
    """Handle M-PESA payment callbacks"""
    try:
        # Get provider
        provider = get_object_or_404(Provider, id=provider_id)
        
        # Parse callback data
        callback_data = json.loads(request.body.decode('utf-8'))
        
        # Process callback
        success = process_payment_callback(provider_id, callback_data)
        
        if success:
            return JsonResponse({
                'ResultCode': 0,
                'ResultDesc': 'Success'
            })
        else:
            return JsonResponse({
                'ResultCode': 1,
                'ResultDesc': 'Failed'
            })
            
    except Exception as e:
        logger.error(f"Error processing M-PESA callback: {e}")
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': 'Error processing callback'
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_provider_callback_url(request, provider_id):
    """Get provider's callback URL"""
    try:
        provider = get_object_or_404(Provider, id=provider_id)
        
        # Generate callback URL if not exists
        if not provider.callback_url:
            from django.conf import settings
            callback_url = f"{settings.FRONTEND_URL}/api/payments/callback/{provider_id}/"
            provider.callback_url = callback_url
            provider.save()
        
        return Response({
            'success': True,
            'callback_url': provider.callback_url,
            'provider_id': provider_id
        })
        
    except Exception as e:
        logger.error(f"Error getting callback URL: {e}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

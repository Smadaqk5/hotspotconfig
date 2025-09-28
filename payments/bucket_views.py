from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import logging

from accounts.models import Provider
from accounts.encryption import encrypt_mpesa_credential, decrypt_mpesa_credential
from .payment_bucket import payment_bucket_service

logger = logging.getLogger(__name__)

def is_provider(user):
    """Check if user is a provider"""
    return user.is_authenticated and (user.user_type == 'provider' or user.is_super_admin)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """Initiate STK Push payment for a provider"""
    try:
        # Get provider from request
        provider = request.user.provider_profile
        
        # Validate required fields
        required_fields = ['phone_number', 'amount', 'account_reference', 'transaction_desc']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate provider has M-PESA credentials
        if not provider.mpesa_consumer_key or not provider.mpesa_consumer_secret:
            return Response({
                'success': False,
                'message': 'M-PESA credentials not configured. Please set up your payment settings.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate credentials are verified
        if not provider.mpesa_credentials_verified:
            return Response({
                'success': False,
                'message': 'M-PESA credentials not verified. Please test your credentials first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initiate STK Push
        result = payment_bucket_service.initiate_stk_push(
            provider_id=provider.id,
            phone_number=request.data['phone_number'],
            amount=request.data['amount'],
            account_reference=request.data['account_reference'],
            transaction_desc=request.data['transaction_desc']
        )
        
        if result.get('ResponseCode') == '0':
            return Response({
                'success': True,
                'message': 'STK Push initiated successfully',
                'checkout_request_id': result.get('CheckoutRequestID'),
                'merchant_request_id': result.get('MerchantRequestID'),
                'customer_message': result.get('CustomerMessage')
            })
        else:
            return Response({
                'success': False,
                'message': result.get('CustomerMessage', 'STK Push failed'),
                'error_code': result.get('ResponseCode')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Payment initiation failed: {e}")
        return Response({
            'success': False,
            'message': f'Payment initiation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_payment_status(request):
    """Query STK Push payment status"""
    try:
        provider = request.user.provider_profile
        
        if 'checkout_request_id' not in request.data:
            return Response({
                'success': False,
                'message': 'checkout_request_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = payment_bucket_service.query_stk_push_status(
            provider_id=provider.id,
            checkout_request_id=request.data['checkout_request_id']
        )
        
        return Response({
            'success': True,
            'status': result.get('ResultCode'),
            'description': result.get('ResultDesc'),
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Payment status query failed: {e}")
        return Response({
            'success': False,
            'message': f'Status query failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_provider_credentials(request):
    """Test provider's M-PESA credentials"""
    try:
        provider = request.user.provider_profile
        
        # Check if credentials are set
        if not provider.mpesa_consumer_key or not provider.mpesa_consumer_secret:
            return Response({
                'success': False,
                'message': 'M-PESA credentials not configured'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Test credentials
        result = payment_bucket_service.test_provider_credentials(provider.id)
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Credential test failed: {e}")
        return Response({
            'success': False,
            'message': f'Credential test failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_provider_callback_url(request, provider_id):
    """Get callback URL for a specific provider"""
    try:
        # Check if user can access this provider
        if not request.user.is_super_admin and request.user.provider_profile.id != provider_id:
            return Response({
                'success': False,
                'message': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        provider = get_object_or_404(Provider, id=provider_id)
        callback_url = payment_bucket_service.generate_callback_url(provider_id)
        
        return Response({
            'success': True,
            'callback_url': callback_url,
            'provider_id': provider_id,
            'provider_name': provider.business_name
        })
        
    except Exception as e:
        logger.error(f"Callback URL generation failed: {e}")
        return Response({
            'success': False,
            'message': f'Callback URL generation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
def mpesa_callback(request, provider_id):
    """Handle M-PESA callback for a specific provider"""
    try:
        # Get provider
        provider = get_object_or_404(Provider, id=provider_id)
        
        # Parse callback data
        try:
            callback_data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        
        # Process callback
        result = payment_bucket_service.handle_mpesa_callback(provider_id, callback_data)
        
        if result['success']:
            logger.info(f"Callback processed successfully for provider {provider_id}")
        else:
            logger.warning(f"Callback processing failed for provider {provider_id}: {result['message']}")
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Callback handling failed for provider {provider_id}: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Callback processing failed: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_mpesa_credentials(request):
    """Save M-PESA credentials for a provider"""
    try:
        provider = request.user.provider_profile
        
        # Validate required fields
        required_fields = ['consumer_key', 'consumer_secret', 'shortcode', 'passkey']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Encrypt and save credentials
        provider.mpesa_consumer_key = encrypt_mpesa_credential(request.data['consumer_key'])
        provider.mpesa_consumer_secret = encrypt_mpesa_credential(request.data['consumer_secret'])
        provider.mpesa_shortcode = request.data['shortcode']
        provider.mpesa_passkey = encrypt_mpesa_credential(request.data['passkey'])
        provider.mpesa_environment = request.data.get('environment', 'sandbox')
        
        # Generate callback URL
        provider.callback_url = payment_bucket_service.generate_callback_url(provider.id)
        
        # Reset verification status
        provider.mpesa_credentials_verified = False
        provider.mpesa_test_status = 'pending'
        
        provider.save()
        
        return Response({
            'success': True,
            'message': 'M-PESA credentials saved successfully',
            'callback_url': provider.callback_url
        })
        
    except Exception as e:
        logger.error(f"Credential save failed: {e}")
        return Response({
            'success': False,
            'message': f'Failed to save credentials: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_mpesa_credentials(request):
    """Clear M-PESA credentials for a provider"""
    try:
        provider = request.user.provider_profile
        
        # Clear credentials
        provider.mpesa_consumer_key = None
        provider.mpesa_consumer_secret = None
        provider.mpesa_shortcode = None
        provider.mpesa_passkey = None
        provider.callback_url = None
        provider.mpesa_credentials_verified = False
        provider.mpesa_test_status = None
        
        provider.save()
        
        return Response({
            'success': True,
            'message': 'M-PESA credentials cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Credential clear failed: {e}")
        return Response({
            'success': False,
            'message': f'Failed to clear credentials: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
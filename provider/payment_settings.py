"""
Provider Payment Settings Views
Handles M-PESA credential configuration for providers
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from accounts.models import Provider
from accounts.encryption import encrypt_mpesa_credential, decrypt_mpesa_credential
from payments.payment_bucket import PaymentBucketService
from django.contrib.auth.decorators import user_passes_test
import json
import logging

logger = logging.getLogger(__name__)

def is_provider(user):
    """Check if user is a provider"""
    return user.is_provider()

@login_required
@user_passes_test(is_provider)
def payment_settings(request):
    """Provider payment settings page"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    context = {
        'page_title': 'Payment Settings',
        'provider': provider,
        'mpesa_configured': bool(provider.mpesa_consumer_key and provider.mpesa_consumer_secret),
        'credentials_verified': provider.mpesa_credentials_verified,
        'test_status': provider.mpesa_test_status,
        'last_test': provider.mpesa_last_test,
        'callback_url': provider.callback_url,
    }
    
    return render(request, 'provider/payment_settings.html', context)

@login_required
@user_passes_test(is_provider)
def save_mpesa_credentials(request):
    """Save M-PESA credentials for provider"""
    if request.method == 'POST':
        try:
            provider = request.user.provider_profile
            
            # Get form data
            consumer_key = request.POST.get('consumer_key', '').strip()
            consumer_secret = request.POST.get('consumer_secret', '').strip()
            shortcode = request.POST.get('shortcode', '').strip()
            passkey = request.POST.get('passkey', '').strip()
            environment = request.POST.get('environment', 'sandbox')
            
            # Validate required fields
            if not all([consumer_key, consumer_secret, shortcode, passkey]):
                messages.error(request, 'All M-PESA credential fields are required.')
                return redirect('provider:payment_settings')
            
            # Encrypt and save credentials
            provider.mpesa_consumer_key = encrypt_mpesa_credential(consumer_key)
            provider.mpesa_consumer_secret = encrypt_mpesa_credential(consumer_secret)
            provider.mpesa_shortcode = shortcode
            provider.mpesa_passkey = encrypt_mpesa_credential(passkey)
            provider.mpesa_environment = environment
            
            # Generate callback URL
            from django.conf import settings
            provider.callback_url = f"{settings.FRONTEND_URL}/api/payments/callback/{provider.id}/"
            
            # Reset verification status
            provider.mpesa_credentials_verified = False
            provider.mpesa_test_status = 'pending'
            
            provider.save()
            
            messages.success(request, 'M-PESA credentials saved successfully. Please test them to verify.')
            return redirect('provider:payment_settings')
            
        except Exception as e:
            logger.error(f"Error saving M-PESA credentials: {e}")
            messages.error(request, 'Error saving credentials. Please try again.')
            return redirect('provider:payment_settings')
    
    return redirect('provider:payment_settings')

@login_required
@user_passes_test(is_provider)
def test_mpesa_credentials(request):
    """Test M-PESA credentials"""
    if request.method == 'POST':
        try:
            provider = request.user.provider_profile
            
            # Check if credentials are configured
            if not provider.mpesa_consumer_key or not provider.mpesa_consumer_secret:
                return JsonResponse({
                    'success': False,
                    'message': 'M-PESA credentials not configured'
                })
            
            # Test credentials
            payment_service = PaymentBucketService(provider.id)
            is_valid = payment_service.test_credentials()
            
            # Refresh provider data
            provider.refresh_from_db()
            
            return JsonResponse({
                'success': is_valid,
                'message': 'Credentials are valid' if is_valid else 'Credentials are invalid',
                'verified': provider.mpesa_credentials_verified,
                'test_status': provider.mpesa_test_status,
                'last_test': provider.mpesa_last_test.isoformat() if provider.mpesa_last_test else None
            })
            
        except Exception as e:
            logger.error(f"Error testing M-PESA credentials: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Error testing credentials'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
@user_passes_test(is_provider)
def clear_mpesa_credentials(request):
    """Clear M-PESA credentials"""
    if request.method == 'POST':
        try:
            provider = request.user.provider_profile
            
            # Clear credentials
            provider.mpesa_consumer_key = None
            provider.mpesa_consumer_secret = None
            provider.mpesa_shortcode = None
            provider.mpesa_passkey = None
            provider.mpesa_credentials_verified = False
            provider.mpesa_test_status = None
            provider.mpesa_last_test = None
            provider.callback_url = None
            
            provider.save()
            
            messages.success(request, 'M-PESA credentials cleared successfully.')
            return redirect('provider:payment_settings')
            
        except Exception as e:
            logger.error(f"Error clearing M-PESA credentials: {e}")
            messages.error(request, 'Error clearing credentials. Please try again.')
            return redirect('provider:payment_settings')
    
    return redirect('provider:payment_settings')

@login_required
@user_passes_test(is_provider)
def get_callback_url(request):
    """Get provider's callback URL"""
    try:
        provider = request.user.provider_profile
        
        # Generate callback URL if not exists
        if not provider.callback_url:
            from django.conf import settings
            callback_url = f"{settings.FRONTEND_URL}/api/payments/callback/{provider.id}/"
            provider.callback_url = callback_url
            provider.save()
        
        return JsonResponse({
            'success': True,
            'callback_url': provider.callback_url
        })
        
    except Exception as e:
        logger.error(f"Error getting callback URL: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Error getting callback URL'
        })

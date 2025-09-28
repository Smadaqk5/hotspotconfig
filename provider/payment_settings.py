from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import logging

from accounts.models import Provider
from accounts.encryption import encrypt_mpesa_credential, decrypt_mpesa_credential
from payments.payment_bucket import payment_bucket_service

logger = logging.getLogger(__name__)

def is_provider(user):
    """Check if user is a provider"""
    return user.is_authenticated and (user.user_type == 'provider' or user.is_super_admin)

@login_required
@user_passes_test(is_provider)
def payment_settings(request):
    """Provider payment settings page"""
    try:
        provider = request.user.provider_profile
    except Provider.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:login')
    
    # Get decrypted credentials for display (masked)
    consumer_key = decrypt_mpesa_credential(provider.mpesa_consumer_key)
    consumer_secret = decrypt_mpesa_credential(provider.mpesa_consumer_secret)
    passkey = decrypt_mpesa_credential(provider.mpesa_passkey)
    
    # Mask credentials for display
    masked_consumer_key = f"{consumer_key[:8]}..." if consumer_key else None
    masked_consumer_secret = f"{consumer_secret[:8]}..." if consumer_secret else None
    masked_passkey = f"{passkey[:8]}..." if passkey else None
    
    context = {
        'page_title': 'Payment Settings',
        'provider': provider,
        'masked_consumer_key': masked_consumer_key,
        'masked_consumer_secret': masked_consumer_secret,
        'masked_passkey': masked_passkey,
        'callback_url': provider.callback_url,
        'credentials_verified': provider.mpesa_credentials_verified,
        'test_status': provider.mpesa_test_status,
        'last_test': provider.mpesa_last_test,
    }
    
    return render(request, 'provider/payment_settings.html', context)

@login_required
@user_passes_test(is_provider)
@require_http_methods(["POST"])
def save_mpesa_credentials(request):
    """Save M-PESA credentials"""
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
        
        # Validate shortcode format
        if not shortcode.isdigit() or len(shortcode) < 5:
            messages.error(request, 'Invalid shortcode format. Please enter a valid Paybill/Till number.')
            return redirect('provider:payment_settings')
        
        # Encrypt and save credentials
        provider.mpesa_consumer_key = encrypt_mpesa_credential(consumer_key)
        provider.mpesa_consumer_secret = encrypt_mpesa_credential(consumer_secret)
        provider.mpesa_shortcode = shortcode
        provider.mpesa_passkey = encrypt_mpesa_credential(passkey)
        provider.mpesa_environment = environment
        
        # Generate callback URL
        provider.callback_url = payment_bucket_service.generate_callback_url(provider.id)
        
        # Reset verification status
        provider.mpesa_credentials_verified = False
        provider.mpesa_test_status = 'pending'
        
        provider.save()
        
        messages.success(request, 'M-PESA credentials saved successfully! Please test your credentials to verify they work.')
        return redirect('provider:payment_settings')
        
    except Exception as e:
        logger.error(f"Failed to save M-PESA credentials: {e}")
        messages.error(request, f'Failed to save credentials: {str(e)}')
        return redirect('provider:payment_settings')

@login_required
@user_passes_test(is_provider)
@require_http_methods(["POST"])
def test_mpesa_credentials(request):
    """Test M-PESA credentials"""
    try:
        provider = request.user.provider_profile
        
        # Check if credentials are set
        if not provider.mpesa_consumer_key or not provider.mpesa_consumer_secret:
            return JsonResponse({
                'success': False,
                'message': 'M-PESA credentials not configured. Please save your credentials first.'
            })
        
        # Test credentials
        result = payment_bucket_service.test_provider_credentials(provider.id)
        
        if result['success']:
            messages.success(request, 'M-PESA credentials are working correctly!')
        else:
            messages.error(request, f'Credential test failed: {result["message"]}')
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Credential test failed: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Credential test failed: {str(e)}'
        })

@login_required
@user_passes_test(is_provider)
@require_http_methods(["POST"])
def clear_mpesa_credentials(request):
    """Clear M-PESA credentials"""
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
        
        messages.success(request, 'M-PESA credentials cleared successfully.')
        return redirect('provider:payment_settings')
        
    except Exception as e:
        logger.error(f"Failed to clear M-PESA credentials: {e}")
        messages.error(request, f'Failed to clear credentials: {str(e)}')
        return redirect('provider:payment_settings')

@login_required
@user_passes_test(is_provider)
def get_callback_url(request):
    """Get callback URL for the provider"""
    try:
        provider = request.user.provider_profile
        
        if not provider.callback_url:
            provider.callback_url = payment_bucket_service.generate_callback_url(provider.id)
            provider.save()
        
        return JsonResponse({
            'success': True,
            'callback_url': provider.callback_url
        })
        
    except Exception as e:
        logger.error(f"Failed to get callback URL: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Failed to get callback URL: {str(e)}'
        })
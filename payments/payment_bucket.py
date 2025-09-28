import requests
import json
import base64
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from accounts.models import Provider
from accounts.encryption import decrypt_mpesa_credential
import logging

logger = logging.getLogger(__name__)

class PaymentBucketService:
    """Payment Bucket service for handling M-PESA transactions across multiple providers"""
    
    def __init__(self):
        self.daraja_base_url = "https://sandbox.safaricom.co.ke" if settings.DEBUG else "https://api.safaricom.co.ke"
    
    def get_provider_access_token(self, provider_id):
        """Get access token for a specific provider using their credentials"""
        try:
            provider = Provider.objects.get(id=provider_id)
            
            # Decrypt provider credentials
            consumer_key = decrypt_mpesa_credential(provider.mpesa_consumer_key)
            consumer_secret = decrypt_mpesa_credential(provider.mpesa_consumer_secret)
            
            if not consumer_key or not consumer_secret:
                raise ValueError("Provider M-PESA credentials not found or invalid")
            
            # Generate access token
            auth_url = f"{self.daraja_base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            # Create basic auth header
            credentials = f"{consumer_key}:{consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(auth_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except Exception as e:
            logger.error(f"Failed to get access token for provider {provider_id}: {e}")
            raise
    
    def initiate_stk_push(self, provider_id, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push for a specific provider"""
        try:
            provider = Provider.objects.get(id=provider_id)
            access_token = self.get_provider_access_token(provider_id)
            
            # Decrypt provider credentials
            shortcode = provider.mpesa_shortcode
            passkey = decrypt_mpesa_credential(provider.mpesa_passkey)
            
            if not shortcode or not passkey:
                raise ValueError("Provider M-PESA shortcode or passkey not found")
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
            
            # STK Push URL
            stk_url = f"{self.daraja_base_url}/mpesa/stkpush/v1/processrequest"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": provider.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            response = requests.post(stk_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Update provider test status
            provider.mpesa_last_test = timezone.now()
            provider.mpesa_test_status = 'success' if result.get('ResponseCode') == '0' else 'failed'
            provider.save()
            
            return result
            
        except Exception as e:
            logger.error(f"STK Push failed for provider {provider_id}: {e}")
            # Update provider test status
            try:
                provider = Provider.objects.get(id=provider_id)
                provider.mpesa_last_test = timezone.now()
                provider.mpesa_test_status = 'failed'
                provider.save()
            except:
                pass
            raise
    
    def query_stk_push_status(self, provider_id, checkout_request_id):
        """Query STK Push status for a specific provider"""
        try:
            access_token = self.get_provider_access_token(provider_id)
            provider = Provider.objects.get(id=provider_id)
            
            query_url = f"{self.daraja_base_url}/mpesa/stkpushquery/v1/query"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(f"{provider.mpesa_shortcode}{decrypt_mpesa_credential(provider.mpesa_passkey)}{timestamp}".encode()).decode()
            
            payload = {
                "BusinessShortCode": provider.mpesa_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(query_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"STK Push query failed for provider {provider_id}: {e}")
            raise
    
    def test_provider_credentials(self, provider_id):
        """Test if provider's M-PESA credentials are working"""
        try:
            # Try to get access token
            access_token = self.get_provider_access_token(provider_id)
            
            if access_token:
                # Update provider status
                provider = Provider.objects.get(id=provider_id)
                provider.mpesa_credentials_verified = True
                provider.mpesa_last_test = timezone.now()
                provider.mpesa_test_status = 'success'
                provider.save()
                
                return {
                    'success': True,
                    'message': 'M-PESA credentials are valid and working',
                    'access_token': access_token[:20] + '...'  # Partial token for verification
                }
            else:
                raise ValueError("Failed to get access token")
                
        except Exception as e:
            logger.error(f"Credential test failed for provider {provider_id}: {e}")
            
            # Update provider status
            try:
                provider = Provider.objects.get(id=provider_id)
                provider.mpesa_credentials_verified = False
                provider.mpesa_last_test = timezone.now()
                provider.mpesa_test_status = 'failed'
                provider.save()
            except:
                pass
            
            return {
                'success': False,
                'message': f'Credential test failed: {str(e)}',
                'error': str(e)
            }
    
    def generate_callback_url(self, provider_id):
        """Generate callback URL for a specific provider"""
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        return f"{base_url}/payments/callback/{provider_id}/"
    
    def handle_mpesa_callback(self, provider_id, callback_data):
        """Handle M-PESA callback for a specific provider"""
        try:
            # Parse callback data
            body = callback_data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            
            # Extract transaction details
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Get callback metadata
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            item_list = callback_metadata.get('Item', [])
            
            # Extract payment details
            payment_data = {}
            for item in item_list:
                name = item.get('Name')
                value = item.get('Value')
                if name and value:
                    payment_data[name] = value
            
            # Process the callback
            if result_code == 0:  # Success
                # Payment successful
                logger.info(f"Payment successful for provider {provider_id}: {checkout_request_id}")
                
                # Here you would typically:
                # 1. Update ticket status to 'paid'
                # 2. Activate WiFi access
                # 3. Send confirmation to customer
                # 4. Update provider revenue tracking
                
                return {
                    'success': True,
                    'message': 'Payment processed successfully',
                    'checkout_request_id': checkout_request_id,
                    'payment_data': payment_data
                }
            else:
                # Payment failed
                logger.warning(f"Payment failed for provider {provider_id}: {result_desc}")
                
                return {
                    'success': False,
                    'message': f'Payment failed: {result_desc}',
                    'result_code': result_code,
                    'result_desc': result_desc
                }
                
        except Exception as e:
            logger.error(f"Callback handling failed for provider {provider_id}: {e}")
            return {
                'success': False,
                'message': f'Callback processing failed: {str(e)}',
                'error': str(e)
            }

# Global service instance
payment_bucket_service = PaymentBucketService()
"""
Payment Bucket API Service for M-PESA Daraja Integration
Handles STK Push payments using provider-specific credentials
"""
import requests
import json
import logging
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from accounts.encryption import decrypt_mpesa_credential
from accounts.models import Provider
from tickets.models import Ticket, TicketSale

logger = logging.getLogger(__name__)

class PaymentBucketService:
    """Service for handling M-PESA payments using provider credentials"""
    
    def __init__(self, provider_id):
        self.provider = Provider.objects.get(id=provider_id)
        self.consumer_key = decrypt_mpesa_credential(self.provider.mpesa_consumer_key)
        self.consumer_secret = decrypt_mpesa_credential(self.provider.mpesa_consumer_secret)
        self.shortcode = self.provider.mpesa_shortcode
        self.passkey = decrypt_mpesa_credential(self.provider.mpesa_passkey)
        self.environment = self.provider.mpesa_environment
        
        # Set base URL based on environment
        if self.environment == 'production':
            self.base_url = "https://api.safaricom.co.ke"
        else:
            self.base_url = "https://sandbox.safaricom.co.ke"
    
    def get_access_token(self):
        """Get M-PESA Daraja API access token"""
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            response = requests.get(
                url,
                auth=(self.consumer_key, self.consumer_secret),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('access_token')
            else:
                logger.error(f"Failed to get access token: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None
    
    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc, callback_url=None):
        """Initiate STK Push payment"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'message': 'Failed to get access token'}
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(timestamp)
            
            # Use provider's callback URL if not provided
            if not callback_url:
                callback_url = self.provider.callback_url or f"{settings.FRONTEND_URL}/api/payments/callback/{self.provider.id}/"
            
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ResponseCode') == '0':
                    return {
                        'success': True,
                        'checkout_request_id': data.get('CheckoutRequestID'),
                        'merchant_request_id': data.get('MerchantRequestID'),
                        'response_code': data.get('ResponseCode'),
                        'response_description': data.get('ResponseDescription')
                    }
                else:
                    return {
                        'success': False,
                        'message': data.get('ResponseDescription', 'STK Push failed')
                    }
            else:
                logger.error(f"STK Push failed: {response.text}")
                return {'success': False, 'message': 'STK Push request failed'}
                
        except Exception as e:
            logger.error(f"Error initiating STK Push: {e}")
            return {'success': False, 'message': str(e)}
    
    def query_stk_push_status(self, checkout_request_id):
        """Query STK Push payment status"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'message': 'Failed to get access token'}
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self._generate_password(timestamp)
            
            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'result_code': data.get('ResultCode'),
                    'result_description': data.get('ResultDesc'),
                    'checkout_request_id': data.get('CheckoutRequestID'),
                    'merchant_request_id': data.get('MerchantRequestID')
                }
            else:
                logger.error(f"STK Push query failed: {response.text}")
                return {'success': False, 'message': 'STK Push query failed'}
                
        except Exception as e:
            logger.error(f"Error querying STK Push status: {e}")
            return {'success': False, 'message': str(e)}
    
    def _generate_password(self, timestamp):
        """Generate M-PESA API password"""
        import base64
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password_bytes = password_string.encode('utf-8')
        password = base64.b64encode(password_bytes).decode('utf-8')
        return password
    
    def test_credentials(self):
        """Test if provider's M-PESA credentials are valid"""
        try:
            access_token = self.get_access_token()
            if access_token:
                # Update provider's test status
                self.provider.mpesa_credentials_verified = True
                self.provider.mpesa_last_test = timezone.now()
                self.provider.mpesa_test_status = 'success'
                self.provider.save()
                return True
            else:
                self.provider.mpesa_credentials_verified = False
                self.provider.mpesa_last_test = timezone.now()
                self.provider.mpesa_test_status = 'failed'
                self.provider.save()
                return False
        except Exception as e:
            logger.error(f"Error testing credentials: {e}")
            self.provider.mpesa_credentials_verified = False
            self.provider.mpesa_last_test = timezone.now()
            self.provider.mpesa_test_status = 'failed'
            self.provider.save()
            return False

def process_payment_callback(provider_id, callback_data):
    """Process M-PESA payment callback"""
    try:
        provider = Provider.objects.get(id=provider_id)
        
        # Extract callback data
        body = callback_data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_description = stk_callback.get('ResultDesc')
        
        if result_code == 0:  # Payment successful
            # Find the ticket sale by checkout request ID
            try:
                ticket_sale = TicketSale.objects.get(
                    provider=provider,
                    payment_reference=checkout_request_id
                )
                
                # Update ticket sale status
                ticket_sale.status = 'completed'
                ticket_sale.payment_reference = checkout_request_id
                ticket_sale.save()
                
                # Activate the ticket
                if ticket_sale.ticket:
                    ticket_sale.ticket.status = 'active'
                    ticket_sale.ticket.save()
                
                logger.info(f"Payment successful for ticket sale {ticket_sale.id}")
                return True
                
            except TicketSale.DoesNotExist:
                logger.error(f"Ticket sale not found for checkout request {checkout_request_id}")
                return False
        else:
            # Payment failed
            try:
                ticket_sale = TicketSale.objects.get(
                    provider=provider,
                    payment_reference=checkout_request_id
                )
                ticket_sale.status = 'failed'
                ticket_sale.save()
                
                logger.info(f"Payment failed for ticket sale {ticket_sale.id}: {result_description}")
                return True
                
            except TicketSale.DoesNotExist:
                logger.error(f"Ticket sale not found for failed payment {checkout_request_id}")
                return False
                
    except Exception as e:
        logger.error(f"Error processing payment callback: {e}")
        return False

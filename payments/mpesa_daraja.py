"""
M-PESA Daraja API integration for customer payments
"""
import requests
import json
import base64
import hashlib
import hmac
from datetime import datetime
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class MpesaDarajaAPI:
    """M-PESA Daraja API integration for STK Push"""
    
    def __init__(self, consumer_key, consumer_secret, environment='sandbox'):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.environment = environment
        
        if environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """Get OAuth access token from Daraja API"""
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            # Create auth string
            auth_string = f"{self.consumer_key}:{self.consumer_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('access_token')
            
        except Exception as e:
            logger.error(f"Failed to get Daraja access token: {e}")
            return None
    
    def initiate_stk_push(self, shortcode, passkey, phone_number, amount, account_reference, transaction_desc, callback_url):
        """Initiate STK Push payment"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None, "Failed to get access token"
            
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            
            # Generate timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Generate password
            password_string = f"{shortcode}{passkey}{timestamp}"
            password_bytes = password_string.encode('ascii')
            password_b64 = base64.b64encode(password_bytes).decode('ascii')
            
            # Format phone number
            if phone_number.startswith('0'):
                phone_number = f"254{phone_number[1:]}"
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = f"254{phone_number}"
            
            payload = {
                "BusinessShortCode": shortcode,
                "Password": password_b64,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data, None
            
        except Exception as e:
            logger.error(f"Failed to initiate STK Push: {e}")
            return None, str(e)
    
    def query_stk_push_status(self, shortcode, passkey, checkout_request_id):
        """Query STK Push status"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None, "Failed to get access token"
            
            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            
            # Generate timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Generate password
            password_string = f"{shortcode}{passkey}{timestamp}"
            password_bytes = password_string.encode('ascii')
            password_b64 = base64.b64encode(password_bytes).decode('ascii')
            
            payload = {
                "BusinessShortCode": shortcode,
                "Password": password_b64,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data, None
            
        except Exception as e:
            logger.error(f"Failed to query STK Push status: {e}")
            return None, str(e)

class CustomerPaymentService:
    """Service for handling customer WiFi payments"""
    
    def __init__(self):
        pass
    
    def initiate_customer_payment(self, provider, phone_number, amount, plan_name):
        """Initiate customer payment using provider's Daraja credentials"""
        try:
            # Decrypt provider's M-PESA credentials
            from accounts.encryption import decrypt_mpesa_credential
            
            consumer_key = decrypt_mpesa_credential(provider.mpesa_consumer_key)
            consumer_secret = decrypt_mpesa_credential(provider.mpesa_consumer_secret)
            passkey = decrypt_mpesa_credential(provider.mpesa_passkey)
            
            if not all([consumer_key, consumer_secret, passkey]):
                return None, "Provider M-PESA credentials not configured"
            
            # Initialize Daraja API
            daraja = MpesaDarajaAPI(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                environment=provider.mpesa_environment
            )
            
            # Generate callback URL
            callback_url = f"{settings.ALLOWED_HOSTS[0]}/api/mpesa/callback/{provider.id}/"
            
            # Initiate STK Push
            result, error = daraja.initiate_stk_push(
                shortcode=provider.mpesa_shortcode,
                passkey=passkey,
                phone_number=phone_number,
                amount=amount,
                account_reference=f"WIFI_{provider.id}",
                transaction_desc=f"WiFi Access - {plan_name}",
                callback_url=callback_url
            )
            
            if error:
                return None, error
            
            # Store pending payment
            from .models import Payment
            payment = Payment.objects.create(
                provider=provider,
                type='mpesa_customer_payment',
                amount=amount,
                currency='KES',
                external_txn_id=result.get('CheckoutRequestID'),
                status='pending',
                provider_payload=result
            )
            
            return result, payment
            
        except Exception as e:
            logger.error(f"Failed to initiate customer payment: {e}")
            return None, str(e)
    
    def handle_daraja_callback(self, provider_id, callback_data):
        """Handle Daraja callback for payment confirmation"""
        try:
            from accounts.models import Provider
            from .models import Payment
            from tickets.models import Ticket, TicketType
            
            provider = Provider.objects.get(id=provider_id)
            
            # Parse callback data
            body = callback_data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Find pending payment
            payment = Payment.objects.filter(
                provider=provider,
                external_txn_id=checkout_request_id,
                status='pending'
            ).first()
            
            if not payment:
                logger.warning(f"Payment not found for checkout request: {checkout_request_id}")
                return False, "Payment not found"
            
            if result_code == 0:  # Success
                # Get transaction details
                callback_metadata = stk_callback.get('CallbackMetadata', {})
                item = callback_metadata.get('Item', [])
                
                # Extract transaction details
                transaction_data = {}
                for item_data in item:
                    name = item_data.get('Name')
                    value = item_data.get('Value')
                    transaction_data[name] = value
                
                # Update payment
                payment.status = 'success'
                payment.provider_payload = callback_data
                payment.save()
                
                # Create WiFi ticket
                ticket = self.create_wifi_ticket(provider, payment, transaction_data)
                
                logger.info(f"Payment successful for provider {provider.business_name}: {payment.amount} KES")
                return True, ticket
                
            else:  # Failed
                payment.status = 'failed'
                payment.provider_payload = callback_data
                payment.save()
                
                logger.warning(f"Payment failed for provider {provider.business_name}: {result_desc}")
                return False, result_desc
                
        except Exception as e:
            logger.error(f"Failed to handle Daraja callback: {e}")
            return False, str(e)
    
    def create_wifi_ticket(self, provider, payment, transaction_data):
        """Create WiFi ticket after successful payment"""
        try:
            from tickets.models import Ticket, TicketType
            import secrets
            import string
            
            # Generate ticket details
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            username = f"user{secrets.randbelow(999999):06d}"
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            
            # Create ticket (you'll need to determine the ticket type based on amount)
            # For now, create a basic time-based ticket
            ticket = Ticket.objects.create(
                provider=provider,
                code=code,
                username=username,
                password=password,
                status='active',
                expires_at=timezone.now() + timezone.timedelta(hours=24),  # 24-hour default
                payment=payment
            )
            
            logger.info(f"Created WiFi ticket {code} for provider {provider.business_name}")
            return ticket
            
        except Exception as e:
            logger.error(f"Failed to create WiFi ticket: {e}")
            return None

"""
Pesapal API integration for provider subscriptions
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

class PesapalAPI:
    """Pesapal API integration for subscription payments"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'PESAPAL_BASE_URL', 'https://cybqa.pesapal.com/pesapalv3/api/')
        self.consumer_key = getattr(settings, 'PESAPAL_CONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'PESAPAL_CONSUMER_SECRET', '')
        self.callback_url = getattr(settings, 'PESAPAL_CALLBACK_URL', '')
        self.ipn_url = getattr(settings, 'PESAPAL_IPN_URL', '')
        
    def get_access_token(self):
        """Get Pesapal access token"""
        try:
            url = f"{self.base_url}Auth/RequestToken"
            
            payload = {
                "consumer_key": self.consumer_key,
                "consumer_secret": self.consumer_secret
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('token')
            
        except Exception as e:
            logger.error(f"Failed to get Pesapal access token: {e}")
            return None
    
    def register_ipn_url(self, access_token):
        """Register IPN URL with Pesapal"""
        try:
            url = f"{self.base_url}URLSetup/RegisterIPN"
            
            payload = {
                "url": self.ipn_url,
                "ipn_notification_type": "GET"
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('ipn_id')
            
        except Exception as e:
            logger.error(f"Failed to register IPN URL: {e}")
            return None
    
    def submit_order(self, access_token, order_data):
        """Submit order to Pesapal"""
        try:
            url = f"{self.base_url}Transactions/SubmitOrderRequest"
            
            payload = {
                "id": order_data['order_id'],
                "currency": order_data.get('currency', 'KES'),
                "amount": order_data['amount'],
                "description": order_data['description'],
                "callback_url": self.callback_url,
                "notification_id": order_data.get('ipn_id'),
                "billing_address": {
                    "phone_number": order_data.get('phone_number', ''),
                    "email_address": order_data.get('email_address', ''),
                    "country_code": order_data.get('country_code', 'KE'),
                    "first_name": order_data.get('first_name', ''),
                    "middle_name": order_data.get('middle_name', ''),
                    "last_name": order_data.get('last_name', ''),
                    "line_1": order_data.get('line_1', ''),
                    "line_2": order_data.get('line_2', ''),
                    "city": order_data.get('city', ''),
                    "state": order_data.get('state', ''),
                    "postal_code": order_data.get('postal_code', ''),
                    "zip_code": order_data.get('zip_code', '')
                }
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('redirect_url')
            
        except Exception as e:
            logger.error(f"Failed to submit order to Pesapal: {e}")
            return None
    
    def get_transaction_status(self, access_token, order_tracking_id):
        """Get transaction status from Pesapal"""
        try:
            url = f"{self.base_url}Transactions/GetTransactionStatus"
            
            params = {
                "orderTrackingId": order_tracking_id
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            return None

class SubscriptionPaymentService:
    """Service for handling provider subscription payments"""
    
    def __init__(self):
        self.pesapal = PesapalAPI()
    
    def initiate_subscription_payment(self, provider, subscription_plan):
        """Initiate subscription payment for provider"""
        try:
            # Get access token
            access_token = self.pesapal.get_access_token()
            if not access_token:
                return None, "Failed to get access token"
            
            # Register IPN URL
            ipn_id = self.pesapal.register_ipn_url(access_token)
            if not ipn_id:
                return None, "Failed to register IPN URL"
            
            # Prepare order data
            order_data = {
                'order_id': f"SUB_{provider.id}_{subscription_plan.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                'amount': float(subscription_plan.price),
                'currency': 'KES',
                'description': f"Subscription: {subscription_plan.name} - {provider.business_name}",
                'ipn_id': ipn_id,
                'phone_number': provider.contact_phone,
                'email_address': provider.contact_email,
                'first_name': provider.contact_person.split()[0] if provider.contact_person else '',
                'last_name': ' '.join(provider.contact_person.split()[1:]) if provider.contact_person and len(provider.contact_person.split()) > 1 else '',
                'country_code': 'KE',
                'line_1': provider.address,
                'city': provider.city,
                'state': provider.county
            }
            
            # Submit order
            redirect_url = self.pesapal.submit_order(access_token, order_data)
            if not redirect_url:
                return None, "Failed to submit order"
            
            # Create subscription record
            from .models import ProviderSubscription
            subscription = ProviderSubscription.objects.create(
                provider=provider,
                plan=subscription_plan,
                status='pending',
                order_id=order_data['order_id'],
                amount=subscription_plan.price,
                currency='KES',
                payment_method='pesapal',
                ipn_id=ipn_id
            )
            
            return redirect_url, subscription
            
        except Exception as e:
            logger.error(f"Failed to initiate subscription payment: {e}")
            return None, str(e)
    
    def handle_payment_callback(self, order_tracking_id, payment_method, payment_account):
        """Handle payment callback from Pesapal"""
        try:
            # Get access token
            access_token = self.pesapal.get_access_token()
            if not access_token:
                return False, "Failed to get access token"
            
            # Get transaction status
            status_data = self.pesapal.get_transaction_status(access_token, order_tracking_id)
            if not status_data:
                return False, "Failed to get transaction status"
            
            # Find subscription
            from .models import ProviderSubscription
            subscription = ProviderSubscription.objects.filter(
                order_id__icontains=order_tracking_id
            ).first()
            
            if not subscription:
                return False, "Subscription not found"
            
            # Update subscription based on status
            if status_data.get('payment_status') == 'COMPLETED':
                subscription.status = 'active'
                subscription.payment_reference = order_tracking_id
                subscription.activated_at = timezone.now()
                
                # Set subscription end date
                if subscription.plan.billing_cycle == 'monthly':
                    subscription.expires_at = timezone.now() + timezone.timedelta(days=30)
                elif subscription.plan.billing_cycle == 'yearly':
                    subscription.expires_at = timezone.now() + timezone.timedelta(days=365)
                
                subscription.save()
                
                # Update provider subscription status
                provider = subscription.provider
                provider.subscription_status = 'active'
                provider.subscription_start_date = timezone.now()
                provider.subscription_end_date = subscription.expires_at
                provider.save()
                
                logger.info(f"Subscription activated for provider {provider.business_name}")
                return True, "Subscription activated successfully"
            
            elif status_data.get('payment_status') == 'FAILED':
                subscription.status = 'failed'
                subscription.save()
                
                logger.warning(f"Subscription payment failed for provider {subscription.provider.business_name}")
                return False, "Payment failed"
            
            else:
                logger.info(f"Payment status: {status_data.get('payment_status')} for order {order_tracking_id}")
                return True, f"Payment status: {status_data.get('payment_status')}"
                
        except Exception as e:
            logger.error(f"Failed to handle payment callback: {e}")
            return False, str(e)
    
    def check_subscription_status(self, subscription):
        """Check subscription status with Pesapal"""
        try:
            if not subscription.order_id:
                return False, "No order ID found"
            
            # Extract order tracking ID from order_id
            order_tracking_id = subscription.order_id.split('_')[-1]
            
            # Get access token
            access_token = self.pesapal.get_access_token()
            if not access_token:
                return False, "Failed to get access token"
            
            # Get transaction status
            status_data = self.pesapal.get_transaction_status(access_token, order_tracking_id)
            if not status_data:
                return False, "Failed to get transaction status"
            
            return True, status_data
            
        except Exception as e:
            logger.error(f"Failed to check subscription status: {e}")
            return False, str(e)

"""
Pesapal API integration
"""
import requests
import json
import base64
import hashlib
import hmac
from django.conf import settings
from django.utils import timezone
from datetime import datetime


class PesapalAPI:
    """Pesapal API client"""
    
    def __init__(self):
        self.consumer_key = settings.PESAPAL_CONSUMER_KEY
        self.consumer_secret = settings.PESAPAL_CONSUMER_SECRET
        self.base_url = settings.PESAPAL_BASE_URL
        self.callback_url = settings.PESAPAL_CALLBACK_URL
        self.ipn_url = settings.PESAPAL_IPN_URL
        
    def get_access_token(self):
        """Get Pesapal access token"""
        url = f"{self.base_url}Auth/RequestToken"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        data = {
            'consumer_key': self.consumer_key,
            'consumer_secret': self.consumer_secret
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def register_ipn(self, access_token):
        """Register IPN URL with Pesapal"""
        url = f"{self.base_url}URLSetup/RegisterIPN"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        data = {
            'url': self.ipn_url,
            'ipn_notification_type': 'GET'
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error registering IPN: {e}")
            return None
    
    def create_order(self, order_data, access_token):
        """Create Pesapal order"""
        url = f"{self.base_url}Transactions/SubmitOrderRequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.post(url, json=order_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating order: {e}")
            return None
    
    def get_order_status(self, order_tracking_id, access_token):
        """Get order status from Pesapal"""
        url = f"{self.base_url}Transactions/GetTransactionStatus"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        data = {
            'orderTrackingId': order_tracking_id
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting order status: {e}")
            return None
    
    def verify_callback(self, order_tracking_id, merchant_reference, payment_reference):
        """Verify Pesapal callback"""
        # This would typically involve signature verification
        # For now, we'll just check if the required fields are present
        return bool(order_tracking_id and merchant_reference and payment_reference)

"""
Test script for Pesapal integration
This script tests the Pesapal payment flow
"""

import requests
import json
import os
from django.conf import settings

# Test configuration
PESAPAL_BASE_URL = "https://cybqa.pesapal.com/pesapalv3/api/"
CONSUMER_KEY = "your-test-consumer-key"
CONSUMER_SECRET = "your-test-consumer-secret"

def test_pesapal_auth():
    """Test Pesapal authentication"""
    print("🔐 Testing Pesapal authentication...")
    
    url = f"{PESAPAL_BASE_URL}Auth/RequestToken"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'consumer_key': CONSUMER_KEY,
        'consumer_secret': CONSUMER_SECRET
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if 'token' in result:
            print("✅ Authentication successful")
            return result['token']
        else:
            print("❌ Authentication failed")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_pesapal_ipn_registration(access_token):
    """Test IPN registration"""
    print("📡 Testing IPN registration...")
    
    url = f"{PESAPAL_BASE_URL}URLSetup/RegisterIPN"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'url': 'https://your-app.herokuapp.com/api/payments/pesapal/ipn/',
        'ipn_notification_type': 'GET'
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if 'ipn_id' in result:
            print("✅ IPN registration successful")
            return result['ipn_id']
        else:
            print("❌ IPN registration failed")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ IPN registration error: {e}")
        return None

def test_pesapal_order_creation(access_token, ipn_id):
    """Test order creation"""
    print("🛒 Testing order creation...")
    
    url = f"{PESAPAL_BASE_URL}Transactions/SubmitOrderRequest"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    order_data = {
        'id': 'TEST-ORDER-001',
        'currency': 'KES',
        'amount': 2500.00,
        'description': 'Test subscription payment',
        'callback_url': 'https://your-app.herokuapp.com/api/payments/pesapal/callback/',
        'cancellation_url': 'https://your-app.herokuapp.com/api/payments/pesapal/callback/?status=cancelled',
        'notification_id': ipn_id,
        'billing_address': {
            'phone_number': '+254700000000',
            'email_address': 'test@example.com',
            'country_code': 'KE',
            'first_name': 'Test',
            'middle_name': '',
            'last_name': 'User',
            'line_1': 'Test Address',
            'line_2': '',
            'city': 'Nairobi',
            'state': 'Nairobi',
            'postal_code': '00100',
            'zip_code': '00100'
        }
    }
    
    try:
        response = requests.post(url, json=order_data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if 'order_tracking_id' in result:
            print("✅ Order creation successful")
            print(f"Order Tracking ID: {result['order_tracking_id']}")
            print(f"Redirect URL: {result.get('redirect_url', 'N/A')}")
            return result
        else:
            print("❌ Order creation failed")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Order creation error: {e}")
        return None

def test_pesapal_order_status(access_token, order_tracking_id):
    """Test order status check"""
    print("📊 Testing order status check...")
    
    url = f"{PESAPAL_BASE_URL}Transactions/GetTransactionStatus"
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
        
        result = response.json()
        print(f"✅ Order status retrieved: {result.get('payment_status', 'Unknown')}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Order status check error: {e}")
        return None

def main():
    """Run all tests"""
    print("🧪 Starting Pesapal Integration Tests")
    print("=" * 50)
    
    # Test 1: Authentication
    access_token = test_pesapal_auth()
    if not access_token:
        print("❌ Cannot proceed without access token")
        return
    
    print()
    
    # Test 2: IPN Registration
    ipn_id = test_pesapal_ipn_registration(access_token)
    if not ipn_id:
        print("❌ Cannot proceed without IPN ID")
        return
    
    print()
    
    # Test 3: Order Creation
    order_result = test_pesapal_order_creation(access_token, ipn_id)
    if not order_result:
        print("❌ Cannot proceed without order")
        return
    
    print()
    
    # Test 4: Order Status Check
    test_pesapal_order_status(access_token, order_result['order_tracking_id'])
    
    print()
    print("🎉 All tests completed!")
    print("=" * 50)
    print("Next steps:")
    print("1. Update your Pesapal credentials in the environment variables")
    print("2. Test the actual payment flow with Pesapal sandbox")
    print("3. Verify webhook handling in your application")

if __name__ == "__main__":
    main()

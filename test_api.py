#!/usr/bin/env python3
"""
API Testing Script for MikroTik Hotspot Config Generator
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_health_check():
    """Test API health check"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_public_endpoints():
    """Test public endpoints"""
    print("\n🔍 Testing public endpoints...")
    
    endpoints = [
        "/public/plans/",
        "/public/models/",
        "/public/voucher-types/",
        "/public/bandwidth-profiles/",
        "/public/templates/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint} - {len(data)} items")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_user_registration():
    """Test user registration"""
    print("\n🔍 Testing user registration...")
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "password_confirm": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+254700000000",
        "company_name": "Test Company"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
        if response.status_code == 201:
            data = response.json()
            print("✅ User registration successful")
            print(f"   Token: {data['token'][:20]}...")
            return data['token']
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login():
    """Test user login"""
    print("\n🔍 Testing user login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ User login successful")
            print(f"   Token: {data['token'][:20]}...")
            return data['token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_authenticated_endpoints(token):
    """Test authenticated endpoints"""
    print("\n🔍 Testing authenticated endpoints...")
    
    headers = {"Authorization": f"Token {token}"}
    
    # Test user info
    try:
        response = requests.get(f"{BASE_URL}/auth/user/", headers=headers)
        if response.status_code == 200:
            print("✅ User info retrieved")
        else:
            print(f"❌ User info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User info error: {e}")
    
    # Test dashboard
    try:
        response = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
        if response.status_code == 200:
            print("✅ Dashboard data retrieved")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    # Test subscription plans
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/plans/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Subscription plans: {len(data)} plans")
        else:
            print(f"❌ Subscription plans failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Subscription plans error: {e}")

def test_config_generation(token):
    """Test configuration generation"""
    print("\n🔍 Testing configuration generation...")
    
    headers = {"Authorization": f"Token {token}"}
    
    # First, get available templates
    try:
        response = requests.get(f"{BASE_URL}/public/templates/")
        if response.status_code == 200:
            templates = response.json()
            if templates:
                template_id = templates[0]['id']
                print(f"✅ Found template: {templates[0]['name']}")
                
                # Test config generation
                config_data = {
                    "template_id": template_id,
                    "config_name": "Test Config",
                    "hotspot_name": "Test Hotspot",
                    "hotspot_ip": "192.168.1.1",
                    "dns_servers": "8.8.8.8,8.8.4.4",
                    "voucher_type_id": 1,
                    "bandwidth_profile_id": 1,
                    "max_users": 50,
                    "voucher_length": 8
                }
                
                response = requests.post(f"{BASE_URL}/generate-config/", 
                                      json=config_data, headers=headers)
                if response.status_code == 201:
                    data = response.json()
                    print("✅ Configuration generated successfully")
                    print(f"   Config ID: {data['config_id']}")
                else:
                    print(f"❌ Config generation failed: {response.status_code}")
                    print(f"   Error: {response.text}")
            else:
                print("❌ No templates available")
        else:
            print(f"❌ Templates failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Config generation error: {e}")

def main():
    """Run all API tests"""
    print("🚀 Starting API Tests for MikroTik Hotspot Config Generator")
    print("=" * 60)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed. Is the server running?")
        sys.exit(1)
    
    # Test public endpoints
    test_public_endpoints()
    
    # Test user registration
    token = test_user_registration()
    if not token:
        # Try login if registration failed
        token = test_user_login()
    
    if token:
        # Test authenticated endpoints
        test_authenticated_endpoints(token)
        
        # Test config generation
        test_config_generation(token)
    else:
        print("\n❌ Could not authenticate. Skipping authenticated tests.")
    
    print("\n" + "=" * 60)
    print("🎉 API testing completed!")
    print("\n📚 For detailed API documentation, see API_DOCUMENTATION.md")
    print("🌐 API Base URL: http://127.0.0.1:8000/api/v1/")

if __name__ == "__main__":
    main()

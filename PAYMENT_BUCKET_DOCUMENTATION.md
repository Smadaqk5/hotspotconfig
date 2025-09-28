# 🚀 Payment Bucket System Documentation

## Overview

The Payment Bucket system is a comprehensive multi-provider M-PESA integration solution that allows multiple hotspot providers to use their own M-PESA Daraja API credentials while your platform handles the technical integration. This creates a scalable, secure, and provider-friendly payment processing system.

## 🏗️ Architecture

### Core Components

1. **Encryption Service** (`accounts/encryption.py`)
   - Secure credential storage using Fernet encryption
   - Environment-based key management
   - Automatic key generation for development

2. **Payment Bucket Service** (`payments/payment_bucket.py`)
   - Multi-provider M-PESA integration
   - Provider-specific credential management
   - STK Push initiation and status tracking
   - Callback handling and processing

3. **API Endpoints** (`payments/bucket_views.py`)
   - RESTful API for payment operations
   - Provider credential testing
   - Payment status queries
   - Callback URL management

4. **Provider Settings UI** (`provider/payment_settings.py`)
   - Secure credential input and management
   - Real-time credential testing
   - Callback URL generation
   - Status monitoring and verification

## 🔐 Security Features

### Credential Encryption
- **Fernet Encryption**: All M-PESA credentials are encrypted before database storage
- **Environment-based Keys**: Production keys managed via environment variables
- **Automatic Key Generation**: Development keys generated automatically
- **Secure Decryption**: Credentials decrypted only when needed for API calls

### Access Control
- **Provider Isolation**: Each provider can only access their own credentials
- **Super Admin Access**: Platform administrators can manage all providers
- **Role-based Permissions**: Strict access control based on user roles

## 🚀 API Endpoints

### Payment Operations

#### Initiate Payment
```http
POST /payments/bucket/initiate/
Content-Type: application/json
Authorization: Token <your-token>

{
    "phone_number": "254712345678",
    "amount": 50,
    "account_reference": "WIFI_001",
    "transaction_desc": "WiFi Access - 1 Hour"
}
```

#### Query Payment Status
```http
POST /payments/bucket/status/
Content-Type: application/json
Authorization: Token <your-token>

{
    "checkout_request_id": "ws_CO_27092024123456789"
}
```

#### Test Provider Credentials
```http
POST /payments/bucket/test-credentials/
Content-Type: application/json
Authorization: Token <your-token>
```

### Callback Handling

#### M-PESA Callback
```http
POST /payments/callback/{provider_id}/
Content-Type: application/json

{
    "Body": {
        "stkCallback": {
            "CheckoutRequestID": "ws_CO_27092024123456789",
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully.",
            "CallbackMetadata": {
                "Item": [
                    {"Name": "Amount", "Value": 50},
                    {"Name": "MpesaReceiptNumber", "Value": "QGH1234567"},
                    {"Name": "PhoneNumber", "Value": "254712345678"}
                ]
            }
        }
    }
}
```

## 🎯 Provider Workflow

### 1. Credential Setup
1. Provider logs into their dashboard
2. Navigates to "Payment Settings"
3. Enters M-PESA Daraja API credentials:
   - Consumer Key
   - Consumer Secret
   - Shortcode (Paybill/Till Number)
   - Passkey
   - Environment (Sandbox/Production)

### 2. Credential Testing
1. Provider clicks "Test Credentials"
2. System validates credentials with M-PESA API
3. Updates verification status
4. Generates callback URL automatically

### 3. Payment Processing
1. Customer selects WiFi plan
2. System initiates STK Push using provider's credentials
3. Customer receives M-PESA prompt
4. Payment goes directly to provider's account
5. Callback confirms transaction
6. WiFi access is activated

## 🔧 Configuration

### Environment Variables

```bash
# Encryption Key (Required for Production)
ENCRYPTION_KEY=your-32-character-encryption-key

# Base URL for Callback URLs
BASE_URL=https://yourdomain.com

# M-PESA Environment
MPESA_ENVIRONMENT=sandbox  # or production
```

### Django Settings

```python
# Encryption key for sensitive data
ENCRYPTION_KEY = config('ENCRYPTION_KEY', default=None)

# Base URL for callback generation
BASE_URL = config('BASE_URL', default='http://localhost:8000')
```

## 📊 Database Schema

### Provider Model Extensions

```python
class Provider(models.Model):
    # ... existing fields ...
    
    # M-PESA Daraja API Credentials (Encrypted)
    mpesa_consumer_key = models.TextField(blank=True, null=True)
    mpesa_consumer_secret = models.TextField(blank=True, null=True)
    mpesa_shortcode = models.CharField(max_length=20, blank=True, null=True)
    mpesa_passkey = models.TextField(blank=True, null=True)
    mpesa_environment = models.CharField(max_length=10, choices=[...], default='sandbox')
    callback_url = models.URLField(blank=True, null=True)
    
    # M-PESA Settings
    mpesa_credentials_verified = models.BooleanField(default=False)
    mpesa_last_test = models.DateTimeField(blank=True, null=True)
    mpesa_test_status = models.CharField(max_length=20, choices=[...], blank=True, null=True)
```

## 🛠️ Implementation Guide

### 1. Install Dependencies
```bash
pip install cryptography>=41.0.0
```

### 2. Set Environment Variables
```bash
export ENCRYPTION_KEY="your-32-character-key"
export BASE_URL="https://yourdomain.com"
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Configure Provider Settings
- Access provider dashboard
- Navigate to Payment Settings
- Enter M-PESA credentials
- Test credentials
- Verify callback URL

## 🔍 Testing

### Credential Testing
```python
# Test provider credentials
result = payment_bucket_service.test_provider_credentials(provider_id)
print(result)
# Output: {'success': True, 'message': 'Credentials are valid', ...}
```

### Payment Initiation
```python
# Initiate STK Push
result = payment_bucket_service.initiate_stk_push(
    provider_id=1,
    phone_number="254712345678",
    amount=50,
    account_reference="WIFI_001",
    transaction_desc="WiFi Access"
)
print(result)
```

### Callback Handling
```python
# Handle M-PESA callback
result = payment_bucket_service.handle_mpesa_callback(
    provider_id=1,
    callback_data=callback_data
)
print(result)
```

## 🚨 Error Handling

### Common Issues

1. **Invalid Credentials**
   - Error: "Credential test failed"
   - Solution: Verify M-PESA credentials in provider settings

2. **Network Timeout**
   - Error: "Request timeout"
   - Solution: Check internet connection and M-PESA API status

3. **Encryption Errors**
   - Error: "Decryption failed"
   - Solution: Verify ENCRYPTION_KEY is set correctly

4. **Callback URL Issues**
   - Error: "Callback URL not accessible"
   - Solution: Ensure BASE_URL is set and server is accessible

## 📈 Benefits

### For Platform Administrators
- **Scalable**: Support unlimited providers
- **Secure**: No access to provider funds
- **Compliant**: Follows M-PESA security standards
- **Maintainable**: Centralized payment processing

### For Providers
- **Direct Revenue**: Money goes to their M-PESA account
- **Easy Setup**: Simple credential configuration
- **Real-time Testing**: Immediate credential verification
- **Secure Storage**: Encrypted credential storage

### for End Users
- **Familiar Payment**: Standard M-PESA STK Push
- **Instant Access**: Immediate WiFi activation
- **Secure Transactions**: Bank-level security

## 🔮 Future Enhancements

1. **Multi-Currency Support**: Support for other payment methods
2. **Advanced Analytics**: Detailed payment analytics
3. **Automated Reconciliation**: Automatic payment reconciliation
4. **Webhook Integration**: Real-time payment notifications
5. **Fraud Detection**: Advanced fraud prevention

## 📞 Support

For technical support or questions about the Payment Bucket system:

1. Check the logs in `django.log`
2. Verify environment variables
3. Test credentials in provider settings
4. Review M-PESA Daraja API documentation
5. Contact system administrator

---

**Note**: This system is designed for production use with proper security measures. Always use HTTPS in production and keep encryption keys secure.

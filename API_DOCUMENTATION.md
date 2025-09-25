# MikroTik Hotspot Config Generator - API Documentation

## 🌐 API Overview

The MikroTik Hotspot Config Generator provides a comprehensive REST API for managing subscriptions, payments, and configuration generation.

**Base URL**: `http://127.0.0.1:8000/api/v1/`

## 🔐 Authentication

The API uses token-based authentication. Include the token in the Authorization header:

```
Authorization: Token your-token-here
```

## 📋 API Endpoints

### Health & Statistics

#### Health Check
```http
GET /api/v1/health/
```
**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "version": "1.0.0",
    "services": {
        "database": "connected",
        "authentication": "active",
        "payments": "ready",
        "config_generation": "ready"
    }
}
```

#### API Statistics
```http
GET /api/v1/stats/
```
**Authentication:** Required
**Response:**
```json
{
    "user_stats": {
        "total_users": 150,
        "verified_users": 120,
        "active_users": 140
    },
    "subscription_stats": {
        "total_plans": 3,
        "active_plans": 3,
        "total_subscriptions": 45,
        "active_subscriptions": 40
    },
    "payment_stats": {
        "total_payments": 200,
        "completed_payments": 180,
        "total_revenue": 450000.00
    },
    "config_stats": {
        "total_configs": 500,
        "user_configs": 25,
        "total_models": 8,
        "total_templates": 5
    }
}
```

### Public Endpoints (No Authentication)

#### Subscription Plans
```http
GET /api/v1/public/plans/
```
**Response:**
```json
[
    {
        "id": 1,
        "name": "Basic",
        "description": "Perfect for small hotspot providers",
        "price": "2500.00",
        "duration_days": 30,
        "is_active": true,
        "features": ["Unlimited config generation", "All MikroTik models"]
    }
]
```

#### MikroTik Models
```http
GET /api/v1/public/models/
```
**Response:**
```json
[
    {
        "id": 1,
        "name": "RB750",
        "model_code": "RB750",
        "description": "5-port router with 1 WAN and 4 LAN ports",
        "is_active": true
    }
]
```

#### Voucher Types
```http
GET /api/v1/public/voucher-types/
```
**Response:**
```json
[
    {
        "id": 1,
        "name": "1 Hour",
        "duration_hours": 1,
        "description": "One hour voucher",
        "is_active": true
    }
]
```

#### Bandwidth Profiles
```http
GET /api/v1/public/bandwidth-profiles/
```
**Response:**
```json
[
    {
        "id": 1,
        "name": "Basic",
        "download_speed": "1M",
        "upload_speed": "512K",
        "description": "Basic internet speed",
        "is_active": true
    }
]
```

#### Config Templates
```http
GET /api/v1/public/templates/
```
**Response:**
```json
[
    {
        "id": 1,
        "name": "Basic Hotspot Setup",
        "description": "Basic hotspot configuration",
        "mikrotik_model": {
            "id": 1,
            "name": "RB750"
        },
        "template_content": "# MikroTik configuration...",
        "is_active": true
    }
]
```

### Authentication

#### User Registration
```http
POST /api/v1/auth/register/
```
**Request:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword",
    "password_confirm": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+254700000000",
    "company_name": "John's ISP"
}
```
**Response:**
```json
{
    "token": "your-auth-token",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

#### User Login
```http
POST /api/v1/auth/login/
```
**Request:**
```json
{
    "email": "john@example.com",
    "password": "securepassword"
}
```
**Response:**
```json
{
    "token": "your-auth-token",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com"
    }
}
```

#### User Logout
```http
POST /api/v1/auth/logout/
```
**Authentication:** Required

#### Get User Info
```http
GET /api/v1/auth/user/
```
**Authentication:** Required

### Subscriptions

#### Get Subscription Plans
```http
GET /api/v1/subscriptions/plans/
```

#### Get Current Subscription
```http
GET /api/v1/subscriptions/current/
```
**Authentication:** Required

#### Create Subscription
```http
POST /api/v1/subscriptions/create/
```
**Authentication:** Required
**Request:**
```json
{
    "plan_id": 1
}
```

### Payments

#### Create Payment
```http
POST /api/v1/payments/create/
```
**Authentication:** Required
**Request:**
```json
{
    "plan_id": 1,
    "amount": "2500.00",
    "currency": "KES",
    "description": "Basic plan subscription"
}
```
**Response:**
```json
{
    "payment": {
        "id": "uuid-here",
        "amount": "2500.00",
        "currency": "KES",
        "status": "pending"
    },
    "checkout_url": "https://pesapal.com/checkout/...",
    "order_tracking_id": "order-123"
}
```

#### Get Payment List
```http
GET /api/v1/payments/list/
```
**Authentication:** Required

#### Get Payment Status
```http
GET /api/v1/payments/status/{payment_id}/
```
**Authentication:** Required

### Configuration Generation

#### Generate Configuration
```http
POST /api/v1/generate-config/
```
**Authentication:** Required
**Request:**
```json
{
    "template_id": 1,
    "config_name": "My Hotspot Config",
    "hotspot_name": "My Hotspot",
    "hotspot_ip": "192.168.1.1",
    "dns_servers": "8.8.8.8,8.8.4.4",
    "voucher_type_id": 1,
    "bandwidth_profile_id": 1,
    "max_users": 50,
    "voucher_length": 8,
    "voucher_prefix": "HOT"
}
```
**Response:**
```json
{
    "config_id": 123,
    "config_content": "# MikroTik configuration...",
    "download_url": "/api/v1/config/download/123/",
    "message": "Configuration generated successfully"
}
```

#### Download Configuration
```http
GET /api/v1/config/download/{config_id}/
```
**Authentication:** Required
**Response:** File download (.rsc file)

#### Get Generated Configs
```http
GET /api/v1/config/generated/
```
**Authentication:** Required

### Dashboard

#### Get Dashboard Data
```http
GET /api/v1/dashboard/
```
**Authentication:** Required
**Response:**
```json
{
    "user": {
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "John's ISP"
    },
    "subscription": {
        "has_subscription": true,
        "plan_name": "Basic",
        "status": "active",
        "is_active": true,
        "days_remaining": 25
    },
    "usage": {
        "configs_generated": 15,
        "last_used": "2024-01-01T10:00:00Z"
    },
    "recent_payments": [...],
    "recent_configs": [...]
}
```

## 🔧 Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include details:
```json
{
    "error": "Error message",
    "details": "Additional error details"
}
```

## 📝 Usage Examples

### Complete Flow Example

1. **Register User**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

2. **Get Available Plans**
```bash
curl http://127.0.0.1:8000/api/v1/public/plans/
```

3. **Create Payment**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/payments/create/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": 1}'
```

4. **Generate Configuration**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/generate-config/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "config_name": "My Config",
    "hotspot_name": "My Hotspot",
    "hotspot_ip": "192.168.1.1",
    "dns_servers": "8.8.8.8",
    "voucher_type_id": 1,
    "bandwidth_profile_id": 1
  }'
```

## 🚀 Rate Limiting

- **Public endpoints**: 100 requests per minute
- **Authenticated endpoints**: 1000 requests per minute
- **Config generation**: 10 requests per minute per user

## 🔒 Security

- All sensitive endpoints require authentication
- Tokens expire after 24 hours
- HTTPS required in production
- Input validation on all endpoints
- SQL injection protection
- XSS protection

## 📊 Monitoring

- Health check endpoint for monitoring
- Detailed error logging
- Performance metrics
- Usage statistics

---

**API Version**: 1.0.0  
**Last Updated**: 2024-01-01  
**Base URL**: `http://127.0.0.1:8000/api/v1/`

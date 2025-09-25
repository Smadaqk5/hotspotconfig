# MikroTik Hotspot Config Generator - Project Structure

## 📁 Project Overview

This is a comprehensive Django-based web application for generating MikroTik hotspot configurations with Pesapal payment integration, designed specifically for Kenyan hotspot providers.

## 🏗️ Architecture

```
hotspot-billing-system/
├── 📁 hotspot_config/           # Django project settings
│   ├── __init__.py
│   ├── settings.py              # Main settings
│   ├── urls.py                  # URL routing
│   ├── wsgi.py                  # WSGI configuration
│   ├── celery.py                # Celery configuration
│   └── security.py              # Security utilities
├── 📁 accounts/                 # User authentication
│   ├── models.py                # User models
│   ├── views.py                 # Auth views
│   ├── serializers.py           # API serializers
│   ├── urls.py                  # Auth URLs
│   └── admin.py                 # Admin interface
├── 📁 subscriptions/            # Subscription management
│   ├── models.py                # Subscription models
│   ├── views.py                 # Subscription views
│   ├── serializers.py           # API serializers
│   ├── urls.py                  # Subscription URLs
│   ├── admin.py                 # Admin interface
│   └── tasks.py                 # Background tasks
├── 📁 payments/                 # Payment processing
│   ├── models.py                # Payment models
│   ├── views.py                 # Payment views
│   ├── serializers.py           # API serializers
│   ├── urls.py                  # Payment URLs
│   ├── admin.py                 # Admin interface
│   └── pesapal.py               # Pesapal integration
├── 📁 config_generator/         # Config generation
│   ├── models.py                # Config models
│   ├── views.py                 # Config views
│   ├── serializers.py           # API serializers
│   ├── urls.py                  # Config URLs
│   └── admin.py                 # Admin interface
├── 📁 dashboard/                # User dashboard
│   ├── views.py                 # Dashboard views
│   └── urls.py                  # Dashboard URLs
├── 📁 templates/                # HTML templates
│   ├── base.html                # Base template
│   ├── index.html               # Landing page
│   └── dashboard.html           # User dashboard
├── 📁 static/                   # Static files
│   └── css/
│       └── input.css             # TailwindCSS input
├── 📁 templates/                # MikroTik templates
│   └── mikrotik_basic_hotspot.rsc
├── 📄 requirements.txt          # Python dependencies
├── 📄 package.json              # Node.js dependencies
├── 📄 Procfile                  # Heroku process file
├── 📄 runtime.txt               # Python version
├── 📄 database_schema.sql       # Database schema
├── 📄 sample_data.sql           # Sample data
├── 📄 env.example               # Environment variables
├── 📄 deploy.sh                 # Linux deployment script
├── 📄 deploy.bat                # Windows deployment script
├── 📄 test_pesapal_integration.py
├── 📄 README.md                 # Project documentation
└── 📄 PROJECT_STRUCTURE.md      # This file
```

## 🔧 Key Components

### 1. **Authentication System** (`accounts/`)
- Custom user model with email verification
- JWT token authentication
- User profiles and company information
- Admin interface for user management

### 2. **Subscription Management** (`subscriptions/`)
- Multiple subscription plans (Basic, Professional, Enterprise)
- Subscription lifecycle management
- Usage tracking and limits
- Background jobs for expiration handling

### 3. **Payment Processing** (`payments/`)
- Pesapal integration for Kenyan payments
- Payment status tracking
- Webhook handling for payment confirmations
- Support for M-Pesa, Airtel Money, and other Kenyan payment methods

### 4. **Config Generation** (`config_generator/`)
- MikroTik model support
- Voucher type management
- Bandwidth profile configuration
- Jinja2 templating for .rsc file generation
- Download and preview functionality

### 5. **User Dashboard** (`dashboard/`)
- Subscription status and usage
- Config generation interface
- Payment history
- Generated configs management

### 6. **Background Tasks** (`subscriptions/tasks.py`)
- Expired subscription checking
- Renewal reminder emails
- Data cleanup and maintenance
- Celery-based task processing

## 🗄️ Database Schema

### Core Tables
- `accounts_user` - Extended user model
- `subscriptions_subscriptionplan` - Available plans
- `subscriptions_subscription` - User subscriptions
- `payments_payment` - Payment records
- `config_generator_generatedconfig` - Generated configs

### Configuration Tables
- `config_generator_mikrotikmodel` - Supported models
- `config_generator_vouchertype` - Voucher durations
- `config_generator_bandwidthprofile` - Bandwidth profiles
- `config_generator_configtemplate` - Config templates

## 🚀 Deployment

### Heroku Configuration
- **Web Dyno**: Django application
- **Worker Dyno**: Celery background tasks
- **PostgreSQL**: Database via Heroku addon
- **Redis**: Celery broker via Heroku addon
- **SendGrid**: Email service via Heroku addon
- **Scheduler**: Background job scheduling

### Environment Variables
- Django settings (SECRET_KEY, DEBUG, etc.)
- Database connection (DATABASE_URL)
- Supabase configuration (SUPABASE_URL, SUPABASE_KEY)
- Pesapal integration (PESAPAL_* variables)
- Email configuration (SENDGRID_API_KEY)
- Redis configuration (REDIS_URL)

## 🔐 Security Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control
- Session management
- Password hashing

### Payment Security
- Pesapal signature verification
- Webhook validation
- Payment status tracking
- Transaction logging

### Data Protection
- Row-level security (RLS) in Supabase
- Input validation and sanitization
- SQL injection prevention
- XSS protection

### Infrastructure Security
- HTTPS enforcement
- Security headers
- Rate limiting
- CORS configuration

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - User information

### Subscriptions
- `GET /api/subscriptions/plans/` - Available plans
- `GET /api/subscriptions/current/` - Current subscription
- `POST /api/subscriptions/create/` - Create subscription

### Payments
- `POST /api/payments/create/` - Create payment
- `GET /api/payments/list/` - Payment history
- `POST /api/payments/pesapal/callback/` - Pesapal callback
- `POST /api/payments/pesapal/ipn/` - Pesapal IPN

### Config Generation
- `GET /api/config/models/` - MikroTik models
- `GET /api/config/voucher-types/` - Voucher types
- `GET /api/config/bandwidth-profiles/` - Bandwidth profiles
- `POST /api/config/generate/` - Generate config
- `GET /api/config/download/{id}/` - Download config

### Dashboard
- `GET /api/dashboard/stats/` - Dashboard statistics
- `GET /api/dashboard/subscription/` - Subscription status

## 🧪 Testing

### Test Files
- `test_pesapal_integration.py` - Pesapal integration tests
- Sample data in `sample_data.sql`
- Database schema in `database_schema.sql`

### Test Scenarios
1. User registration and authentication
2. Subscription creation and management
3. Payment processing with Pesapal
4. Config generation and download
5. Background job execution
6. Admin panel functionality

## 📊 Monitoring & Maintenance

### Background Jobs
- Daily subscription expiration checks
- Renewal reminder emails
- Data cleanup and archiving
- Usage statistics generation

### Logging
- Django application logs
- Celery task logs
- Payment transaction logs
- Error tracking and monitoring

### Performance
- Database query optimization
- Caching strategies
- Static file serving
- CDN integration

## 🔄 Development Workflow

### Local Development
1. Clone repository
2. Install dependencies
3. Set up environment variables
4. Run migrations
5. Load sample data
6. Start development server

### Deployment
1. Set up Heroku app
2. Configure addons
3. Set environment variables
4. Deploy application
5. Run migrations
6. Set up background jobs

### Maintenance
1. Monitor application logs
2. Check subscription status
3. Verify payment processing
4. Update dependencies
5. Backup database

## 📈 Scalability Considerations

### Horizontal Scaling
- Multiple web dynos
- Redis clustering
- Database read replicas
- CDN for static assets

### Vertical Scaling
- Upgrade dyno types
- Increase database resources
- Optimize query performance
- Implement caching

### Cost Optimization
- Efficient resource usage
- Background job optimization
- Database query optimization
- Static asset optimization

---

**This project structure provides a solid foundation for a production-ready MikroTik hotspot configuration generator with comprehensive features for Kenyan hotspot providers.**

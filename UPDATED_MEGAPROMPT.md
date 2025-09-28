# 🚀 MikroTik Hotspot Platform - Updated MegaPrompt

## 🎯 **Platform Overview**

A multi-tenant hotspot management platform with **two distinct payment flows**:
1. **Provider Subscriptions** → Platform revenue via Pesapal
2. **Customer WiFi Payments** → Provider revenue via M-PESA Daraja

## 💰 **Payment Architecture**

### **Flow 1: Provider Subscriptions (Platform Revenue)**
```
Provider → Subscribe Button → Pesapal Checkout → Platform Account
    ↓
Monthly/Yearly subscription fees → Your Pesapal merchant account
```

### **Flow 2: Customer WiFi Payments (Provider Revenue)**
```
Customer → Captive Portal → M-PESA STK Push → Provider's M-PESA Account
    ↓
WiFi voucher purchase → Direct to Provider's mobile money
```

## 🏗 **System Architecture**

### **Multi-Tenant Design**
- **Super Admin**: Platform oversight and provider management
- **Providers**: Hotspot business owners with their own M-PESA credentials
- **Customers**: End users accessing WiFi (no platform registration)

### **Database Schema**
```sql
-- Providers table with dual payment credentials
providers (
  id uuid PRIMARY KEY,
  business_name TEXT,
  contact_email TEXT,
  -- Pesapal subscription (platform revenue)
  pesapal_merchant_id TEXT,
  -- M-PESA Daraja credentials (provider revenue)
  mpesa_consumer_key TEXT,      -- encrypted
  mpesa_consumer_secret TEXT,    -- encrypted
  mpesa_shortcode TEXT,
  mpesa_passkey TEXT,           -- encrypted
  mpesa_callback_path TEXT,     -- /api/mpesa/callback/{provider_id}
  created_at timestamptz
);

-- Provider subscriptions (platform revenue tracking)
provider_subscriptions (
  id uuid PRIMARY KEY,
  provider_id uuid REFERENCES providers(id),
  status TEXT, -- 'active','expired','pending'
  start_date timestamptz,
  expiry_date timestamptz,
  pesapal_txn_id TEXT,
  amount numeric(10,2),
  created_at timestamptz
);

-- Unified payments table (both flows)
payments (
  id uuid PRIMARY KEY,
  provider_id uuid REFERENCES providers(id),
  type TEXT, -- 'pesapal_provider_subscription' | 'mpesa_customer_payment'
  provider_payload jsonb, -- raw webhook data for auditing
  amount numeric(10,2),
  currency TEXT DEFAULT 'KES',
  external_txn_id TEXT, -- pesapal or mpesa transaction id
  status TEXT, -- 'pending','success','failed'
  created_at timestamptz
);

-- WiFi vouchers/tickets
tickets (
  id uuid PRIMARY KEY,
  provider_id uuid REFERENCES providers(id),
  code TEXT UNIQUE,
  username TEXT,
  password TEXT,
  plan_type TEXT, -- 'time' or 'data'
  duration_hours INTEGER,
  data_limit_mb INTEGER,
  price numeric(10,2),
  status TEXT, -- 'active','used','expired'
  expires_at timestamptz,
  created_at timestamptz
);
```

## 🔌 **API Endpoints**

### **Provider Subscription Flow**
```
POST /api/providers/{id}/pesapal/create-order
GET  /api/payments/pesapal/callback
POST /api/payments/pesapal/webhook
GET  /api/providers/{id}/subscription-status
```

### **Customer Payment Flow**
```
POST /api/captive/{provider_id}/initiate-mpesa
POST /api/mpesa/callback/{provider_id}
GET  /api/tickets/{code}/status
POST /api/tickets/{code}/activate
```

## 🎨 **User Interfaces**

### **1. Super Admin Dashboard**
- **Global Analytics**: Total providers, platform revenue, system health
- **Provider Management**: Approve, suspend, view provider details
- **Revenue Tracking**: Pesapal subscription revenue analytics
- **System Monitoring**: Payment success rates, provider performance

### **2. Provider Dashboard**
- **Subscription Management**: View/upgrade Pesapal subscription
- **M-PESA Settings**: Configure Daraja credentials (encrypted storage)
- **Ticket Management**: Generate and monitor WiFi vouchers
- **Revenue Analytics**: Customer payment tracking
- **MikroTik Config**: Download router configuration files

### **3. Captive Portal (Customer-Facing)**
- **Plan Selection**: Time-based and data-based WiFi plans
- **M-PESA Payment**: STK Push with provider's credentials
- **Ticket Display**: WiFi credentials after successful payment
- **No Registration**: Seamless customer experience

## 🔐 **Security Implementation**

### **Data Encryption**
- **M-PESA Credentials**: Encrypted at rest using Fernet encryption
- **API Keys**: Stored as Heroku config variables
- **Webhook Verification**: Signature validation for Pesapal and Daraja

### **Access Control**
- **Provider Isolation**: Each provider only sees their own data
- **Role-Based Permissions**: Super Admin, Provider, Customer access levels
- **Rate Limiting**: STK Push endpoint protection against abuse

## 🚀 **Deployment Architecture**

### **Heroku Configuration**
```bash
# Platform settings
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app.herokuapp.com

# Encryption
ENCRYPTION_KEY=your-fernet-encryption-key

# Pesapal (Platform Revenue)
PESAPAL_CONSUMER_KEY=your-pesapal-key
PESAPAL_CONSUMER_SECRET=your-pesapal-secret
PESAPAL_CALLBACK_URL=https://your-app.herokuapp.com/api/payments/pesapal/callback
PESAPAL_IPN_URL=https://your-app.herokuapp.com/api/payments/pesapal/webhook

# Database
DATABASE_URL=postgresql://...
```

### **Automation Tasks**
- **Heroku Scheduler**: Daily subscription expiry checks
- **Ticket Cleanup**: Automatic expired ticket management
- **Revenue Reports**: Monthly analytics generation
- **Security Audits**: Regular credential rotation

## 📊 **Business Model**

### **Platform Revenue (Pesapal)**
- **Monthly Subscriptions**: $10-50 per provider
- **Annual Plans**: Discounted yearly subscriptions
- **Premium Features**: Advanced analytics, API access

### **Provider Revenue (M-PESA)**
- **Direct Payments**: 100% of customer payments go to provider
- **No Platform Fees**: Zero commission on customer transactions
- **Provider Control**: Full control over pricing and plans

## 🎯 **Key Features**

### **For Super Admins**
- **Global Dashboard**: Platform-wide analytics and management
- **Provider Onboarding**: Automated approval workflow
- **Revenue Tracking**: Pesapal subscription analytics
- **System Health**: Payment success monitoring

### **For Providers**
- **Easy Setup**: Quick M-PESA credential configuration
- **Direct Revenue**: All customer payments go to their account
- **Analytics**: Customer usage and revenue tracking
- **Router Integration**: MikroTik configuration generation

### **For Customers**
- **Seamless Access**: No registration required
- **Mobile Payments**: M-PESA STK Push integration
- **Instant WiFi**: Automatic access after payment
- **Secure Transactions**: Encrypted payment processing

## 🔄 **Payment Flows**

### **Provider Subscription (Pesapal)**
1. Provider clicks "Subscribe" in dashboard
2. Platform creates Pesapal order with provider metadata
3. Provider completes payment via Pesapal checkout
4. Pesapal webhook confirms payment
5. Platform activates provider subscription
6. **Money goes to platform's Pesapal account**

### **Customer WiFi Payment (M-PESA)**
1. Customer selects plan on captive portal
2. Platform uses provider's Daraja credentials for STK Push
3. Customer confirms payment on phone
4. Daraja webhook confirms transaction
5. Platform creates and activates WiFi voucher
6. **Money goes directly to provider's M-PESA account**

## 🎉 **Success Metrics**

### **Platform KPIs**
- **Provider Growth**: Monthly new provider signups
- **Subscription Revenue**: Pesapal payment tracking
- **System Uptime**: 99.9% availability target
- **Payment Success**: >95% transaction success rate

### **Provider KPIs**
- **Customer Payments**: M-PESA transaction volume
- **Ticket Usage**: WiFi voucher redemption rates
- **Revenue Growth**: Monthly customer payment trends
- **System Performance**: Router uptime and speed

---

## 🚀 **Ready for Production**

This updated MegaPrompt provides a complete, scalable platform that:
- ✅ **Separates revenue streams** (platform vs provider)
- ✅ **Ensures provider control** over their customer payments
- ✅ **Provides platform oversight** through subscription management
- ✅ **Maintains security** with encrypted credentials
- ✅ **Scales infinitely** with multi-tenant architecture

The platform is now ready for immediate deployment and can serve unlimited providers with their own M-PESA credentials while generating platform revenue through Pesapal subscriptions!

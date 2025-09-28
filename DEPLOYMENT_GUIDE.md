# 🚀 MikroTik Hotspot Platform - Complete Deployment Guide

## 📋 Overview

This guide covers deploying the complete MikroTik Hotspot Platform to Heroku with all features:
- **Super Admin Dashboard** - Global platform management
- **Provider Dashboard** - Multi-tenant provider management
- **Captive Portal** - Customer-facing WiFi access
- **Payment Integration** - M-PESA Daraja + Pesapal
- **MikroTik Integration** - Router configuration generation
- **Automation** - Heroku Scheduler tasks

## 🛠 Prerequisites

### Required Accounts
- [ ] **Heroku Account** - [heroku.com](https://heroku.com)
- [ ] **GitHub Account** - [github.com](https://github.com)
- [ ] **Supabase Account** - [supabase.com](https://supabase.com) (for PostgreSQL)
- [ ] **Pesapal Account** - [pesapal.com](https://pesapal.com) (for payments)
- [ ] **M-PESA Daraja API** - [developer.safaricom.co.ke](https://developer.safaricom.co.ke)

### Required Tools
- [ ] **Git** - [git-scm.com](https://git-scm.com)
- [ ] **Heroku CLI** - [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
- [ ] **Python 3.11+** - [python.org](https://python.org)

## 🗄 Database Setup (Supabase)

### 1. Create Supabase Project
```bash
# Go to supabase.com and create a new project
# Note down your project URL and API keys
```

### 2. Configure Database
```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set up Row Level Security (RLS)
ALTER TABLE accounts_provider ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets_ticket ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments_payment ENABLE ROW LEVEL SECURITY;
```

## 🚀 Heroku Deployment

### 1. Create Heroku App
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-hotspot-platform

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini
```

### 2. Configure Environment Variables
```bash
# Set environment variables
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app.herokuapp.com"
heroku config:set ENCRYPTION_KEY="your-encryption-key-here"

# Database
heroku config:set DATABASE_URL="$(heroku config:get DATABASE_URL)"

# Pesapal Configuration
heroku config:set PESAPAL_CONSUMER_KEY="your-pesapal-key"
heroku config:set PESAPAL_CONSUMER_SECRET="your-pesapal-secret"
heroku config:set PESAPAL_CALLBACK_URL="https://your-app.herokuapp.com/payments/pesapal/callback/"
heroku config:set PESAPAL_IPN_URL="https://your-app.herokuapp.com/payments/pesapal/ipn/"

# Email Configuration (Optional)
heroku config:set EMAIL_HOST="smtp.gmail.com"
heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="your-app-password"
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True

# Supabase Configuration (if using)
heroku config:set SUPABASE_URL="your-supabase-url"
heroku config:set SUPABASE_KEY="your-supabase-key"
heroku config:set SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

### 3. Deploy to Heroku
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Add Heroku remote
heroku git:remote -a your-hotspot-platform

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Collect static files
heroku run python manage.py collectstatic --noinput
```

## 🔧 Post-Deployment Configuration

### 1. Set Up Heroku Scheduler
```bash
# Add Heroku Scheduler addon
heroku addons:create scheduler:standard

# Configure scheduled tasks in Heroku Dashboard:
# - Daily at 2 AM: python manage.py run_tasks --task=expire_subscriptions
# - Daily at 3 AM: python manage.py run_tasks --task=cleanup_tickets
# - Daily at 4 AM: python manage.py run_tasks --task=cleanup_data
# - Weekly on Monday at 5 AM: python manage.py run_tasks --task=usage_reports
```

### 2. Configure Domain (Optional)
```bash
# Add custom domain
heroku domains:add your-domain.com

# Configure DNS
# Add CNAME record: www -> your-app.herokuapp.com
```

### 3. Set Up SSL
```bash
# Heroku provides SSL automatically for *.herokuapp.com domains
# For custom domains, use Heroku SSL addon
heroku addons:create ssl:endpoint
```

## 📱 M-PESA Daraja API Setup

### 1. Register for Daraja API
1. Go to [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create an account and register your app
3. Get your Consumer Key and Consumer Secret
4. Set up your callback URLs

### 2. Configure Callback URLs
```
# For each provider, the system will generate:
https://your-app.herokuapp.com/captive-portal/callback/{provider_id}/

# Add these to your Daraja API configuration
```

### 3. Test M-PESA Integration
```bash
# Test the payment bucket system
heroku run python manage.py shell
>>> from payments.payment_bucket import payment_bucket_service
>>> # Test with sandbox credentials
```

## 💳 Pesapal Integration Setup

### 1. Register with Pesapal
1. Go to [pesapal.com](https://pesapal.com)
2. Create a merchant account
3. Get your Consumer Key and Consumer Secret
4. Configure your callback URLs

### 2. Configure Callback URLs
```
# Set in your environment variables:
PESAPAL_CALLBACK_URL=https://your-app.herokuapp.com/subscriptions/callback/
PESAPAL_IPN_URL=https://your-app.herokuapp.com/subscriptions/ipn/
```

## 🔐 Security Configuration

### 1. Content Security Policy
The platform includes a custom CSP middleware that:
- Allows inline scripts for the captive portal
- Prevents XSS attacks
- Ensures secure payment processing

### 2. Data Encryption
- M-PESA credentials are encrypted using Fernet encryption
- Encryption key is stored in environment variables
- All sensitive data is encrypted at rest

### 3. Access Control
- Super Admin: Full platform access
- Provider: Own data only
- End Users: No web access (captive portal only)

## 📊 Monitoring and Analytics

### 1. Heroku Metrics
```bash
# View app metrics
heroku logs --tail
heroku ps
heroku config
```

### 2. Database Monitoring
```bash
# Check database status
heroku pg:info
heroku pg:psql
```

### 3. Custom Analytics
The platform includes built-in analytics for:
- Provider performance
- Revenue tracking
- Ticket usage statistics
- System health monitoring

## 🚨 Troubleshooting

### Common Issues

#### 1. Migration Errors
```bash
# Reset migrations if needed
heroku run python manage.py migrate --fake-initial
```

#### 2. Static Files Not Loading
```bash
# Recollect static files
heroku run python manage.py collectstatic --noinput
```

#### 3. Database Connection Issues
```bash
# Check database status
heroku pg:info
heroku pg:psql
```

#### 4. Payment Integration Issues
- Verify M-PESA credentials are correct
- Check callback URLs are accessible
- Ensure Pesapal credentials are valid

### Debug Mode
```bash
# Enable debug mode temporarily
heroku config:set DEBUG=True
heroku restart
```

## 📈 Scaling and Performance

### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_tickets_provider_status ON tickets_ticket(provider_id, status);
CREATE INDEX idx_payments_provider_status ON payments_payment(provider_id, status);
CREATE INDEX idx_subscriptions_provider_status ON subscriptions_providersubscription(provider_id, status);
```

### 2. Caching
```bash
# Add Redis for caching
heroku addons:create heroku-redis:mini
```

### 3. CDN for Static Files
```bash
# Add CloudFront or similar CDN for static files
```

## 🔄 Backup and Recovery

### 1. Database Backups
```bash
# Create database backup
heroku pg:backups:capture

# Download backup
heroku pg:backups:download
```

### 2. Automated Backups
```bash
# Set up automated daily backups
heroku addons:create pgbackups:auto-week
```

## 📞 Support and Maintenance

### 1. Log Monitoring
```bash
# Monitor logs in real-time
heroku logs --tail --app your-hotspot-platform
```

### 2. Performance Monitoring
```bash
# Check app performance
heroku ps:scale web=1
heroku ps:restart
```

### 3. Regular Maintenance
- Monitor database performance
- Check payment integration status
- Review security logs
- Update dependencies regularly

## 🎯 Production Checklist

### Pre-Launch
- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Super user created
- [ ] M-PESA integration tested
- [ ] Pesapal integration tested
- [ ] SSL certificate active
- [ ] Domain configured (if applicable)
- [ ] Monitoring set up

### Post-Launch
- [ ] Test all user flows
- [ ] Verify payment processing
- [ ] Check automated tasks
- [ ] Monitor performance
- [ ] Set up alerts
- [ ] Create documentation for users

## 📚 Additional Resources

### Documentation
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
- [M-PESA Daraja API Documentation](https://developer.safaricom.co.ke/docs)

### Support
- Platform Support: support@hotspotplatform.com
- Technical Issues: tech@hotspotplatform.com
- Billing Support: billing@hotspotplatform.com

---

## 🎉 Congratulations!

Your MikroTik Hotspot Platform is now fully deployed and ready for production use! The platform includes:

✅ **Multi-tenant architecture** with provider isolation  
✅ **Payment integration** with M-PESA and Pesapal  
✅ **Captive portal** for customer WiFi access  
✅ **MikroTik integration** with config generation  
✅ **Super admin oversight** with global analytics  
✅ **Automated tasks** for maintenance  
✅ **Security features** with encryption and CSP  

The platform is now ready to serve hotspot providers and their customers!
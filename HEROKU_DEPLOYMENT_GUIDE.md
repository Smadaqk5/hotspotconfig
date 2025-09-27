# MikroTik Hotspot Multi-Level Platform - Heroku Deployment Guide

## Overview
This guide will help you deploy the complete MikroTik Hotspot Multi-Level Platform to Heroku with Supabase as the database and Pesapal for payments.

## Prerequisites
- Heroku CLI installed
- Git repository set up
- Supabase account
- Pesapal account
- SendGrid account (for emails)

## Step 1: Prepare Your Application

### 1.1 Update Requirements
Ensure your `requirements.txt` includes all necessary packages:

```txt
# Django and Core Dependencies
Django>=4.2.0,<5.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
whitenoise>=6.0.0
dj-database-url>=2.0.0
python-decouple>=3.8

# Database
psycopg2-binary>=2.9.0

# Image processing
Pillow>=10.0.0

# Celery for Background Tasks
celery>=5.3.0
redis>=4.5.0

# HTTP Requests
requests>=2.31.0

# Security
cryptography>=41.0.0

# Production Server
gunicorn>=21.0.0

# Development and Testing
pytest>=7.0.0
pytest-django>=4.5.0
flake8>=5.0.0
bandit>=1.7.0
safety>=2.0.0
coverage>=6.0.0
```

### 1.2 Update Settings for Production
Update `hotspot_config/settings.py`:

```python
import os
from decouple import config
import dj_database_url

# ... existing code ...

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@yourdomain.com')

# Celery settings
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'
```

### 1.3 Create Procfile
Create `Procfile` in the root directory:

```
web: gunicorn hotspot_config.wsgi --log-file -
worker: celery -A hotspot_config worker --loglevel=info
```

### 1.4 Create Runtime File
Create `runtime.txt`:

```
python-3.11.0
```

## Step 2: Set Up Supabase Database

### 2.1 Create Supabase Project
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Note down your project URL and API keys

### 2.2 Get Database URL
1. Go to Settings > Database
2. Copy the connection string
3. Format: `postgresql://postgres.abcdefghijklmnop:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

## Step 3: Set Up Pesapal Integration

### 3.1 Get Pesapal Credentials
1. Register at [Pesapal](https://pesapal.com)
2. Get your Consumer Key and Consumer Secret
3. Set up your callback URLs

### 3.2 Configure Pesapal Settings
Update your environment variables with Pesapal credentials.

## Step 4: Deploy to Heroku

### 4.1 Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit"
```

### 4.2 Create Heroku App
```bash
heroku create your-app-name
```

### 4.3 Set Environment Variables
```bash
# Django settings
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"

# Database
heroku config:set DATABASE_URL="postgresql://postgres.abcdefghijklmnop:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# Supabase
heroku config:set SUPABASE_URL="https://your-project.supabase.co"
heroku config:set SUPABASE_KEY="your-supabase-key"
heroku config:set SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# Pesapal
heroku config:set PESAPAL_CONSUMER_KEY="your-consumer-key"
heroku config:set PESAPAL_CONSUMER_SECRET="your-consumer-secret"
heroku config:set PESAPAL_BASE_URL="https://www.pesapal.com/api"
heroku config:set PESAPAL_CALLBACK_URL="https://your-app-name.herokuapp.com/payments/callback/"
heroku config:set PESAPAL_IPN_URL="https://your-app-name.herokuapp.com/payments/ipn/"

# Email (SendGrid)
heroku config:set EMAIL_HOST="smtp.sendgrid.net"
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER="apikey"
heroku config:set EMAIL_HOST_PASSWORD="your-sendgrid-api-key"
heroku config:set DEFAULT_FROM_EMAIL="noreply@yourdomain.com"

# Redis (for Celery)
heroku config:set REDIS_URL="redis://localhost:6379"

# Frontend URL
heroku config:set FRONTEND_URL="https://your-app-name.herokuapp.com"
```

### 4.4 Deploy to Heroku
```bash
git push heroku main
```

### 4.5 Run Migrations
```bash
heroku run python manage.py migrate
```

### 4.6 Create Superuser
```bash
heroku run python manage.py createsuperuser
```

### 4.7 Collect Static Files
```bash
heroku run python manage.py collectstatic --noinput
```

## Step 5: Set Up Background Tasks

### 5.1 Install Heroku Scheduler Add-on
```bash
heroku addons:create scheduler:standard
```

### 5.2 Configure Scheduled Tasks
Go to Heroku Scheduler dashboard and add these tasks:

1. **Daily Expiry Check** (runs daily at 2:00 AM):
   ```bash
   python manage.py shell -c "from subscriptions.tasks import check_expired_subscriptions, check_expired_tickets; check_expired_subscriptions.delay(); check_expired_tickets.delay()"
   ```

2. **Daily Reminders** (runs daily at 9:00 AM):
   ```bash
   python manage.py shell -c "from subscriptions.tasks import send_daily_reminders; send_daily_reminders.delay()"
   ```

3. **Daily Reports** (runs daily at 6:00 PM):
   ```bash
   python manage.py shell -c "from subscriptions.tasks import generate_daily_reports; generate_daily_reports.delay()"
   ```

4. **Weekly Cleanup** (runs weekly on Sunday at 3:00 AM):
   ```bash
   python manage.py shell -c "from subscriptions.tasks import cleanup_expired_data; cleanup_expired_data.delay()"
   ```

## Step 6: Configure Custom Domain (Optional)

### 6.1 Add Custom Domain
```bash
heroku domains:add yourdomain.com
```

### 6.2 Update DNS
Point your domain to Heroku:
- CNAME: `www` → `your-app-name.herokuapp.com`
- A Record: `@` → `your-app-name.herokuapp.com`

## Step 7: Set Up Monitoring

### 7.1 Install New Relic (Optional)
```bash
heroku addons:create newrelic:wayne
```

### 7.2 Set Up Logging
```bash
heroku logs --tail
```

## Step 8: Test Your Deployment

### 8.1 Test Basic Functionality
1. Visit your Heroku app URL
2. Test user registration
3. Test provider registration
4. Test ticket generation
5. Test payment processing

### 8.2 Test Background Tasks
1. Check Heroku Scheduler logs
2. Verify email notifications
3. Test subscription expiry

## Step 9: Production Optimizations

### 9.1 Enable HTTPS
Heroku automatically provides HTTPS for all apps.

### 9.2 Set Up CDN (Optional)
Consider using CloudFlare for better performance.

### 9.3 Database Optimization
- Set up database connection pooling
- Monitor query performance
- Set up database backups

## Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   - Run `heroku run python manage.py collectstatic --noinput`
   - Check `STATICFILES_STORAGE` setting

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is correct
   - Check Supabase connection settings

3. **Email Not Sending**
   - Verify SendGrid API key
   - Check email settings in Heroku config

4. **Background Tasks Not Running**
   - Check Heroku Scheduler configuration
   - Verify Celery worker is running

### Useful Commands

```bash
# Check app status
heroku ps

# View logs
heroku logs --tail

# Run Django shell
heroku run python manage.py shell

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Restart app
heroku restart
```

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS
- [ ] Set up proper CORS settings
- [ ] Use environment variables for secrets
- [ ] Set up database backups
- [ ] Monitor for security vulnerabilities

## Performance Optimization

- [ ] Enable database connection pooling
- [ ] Use CDN for static files
- [ ] Optimize database queries
- [ ] Set up caching
- [ ] Monitor app performance
- [ ] Set up logging and monitoring

## Support

For issues and support:
1. Check Heroku logs: `heroku logs --tail`
2. Check Django logs in your app
3. Verify environment variables
4. Test locally with production settings

## Next Steps

After successful deployment:
1. Set up monitoring and alerting
2. Configure automated backups
3. Set up staging environment
4. Implement CI/CD pipeline
5. Set up performance monitoring
6. Plan for scaling

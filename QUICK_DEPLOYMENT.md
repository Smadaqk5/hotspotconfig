# 🚀 Quick Heroku Deployment Guide

## 📋 **Environment Variables to Set**

Copy and paste these commands one by one in your terminal:

```bash
# Django Settings
heroku config:set SECRET_KEY="stIxCFY89xrhHr3T5lguRB1W1SnSTCy0zDxHXC1gr0o2nI95znL6PrDJywTmuRblpSU"
heroku config:set DEBUG="False"
heroku config:set ALLOWED_HOSTS="hotspott-39e105144510.herokuapp.com"

# Database (Supabase PostgreSQL)
heroku config:set DATABASE_URL="postgresql://postgres.vbrkdpjaplqrngarnhyu:C7kCNrGZa$E8S7W@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
heroku config:set SUPABASE_URL="https://vbrkdpjaplqrngarnhyu.supabase.co"
heroku config:set SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZicmtkcGphcGxxcm5nYXJnaHl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5NTM1NjUsImV4cCI6MjA3NDUyOTU2NX0.6GD8quMGFMl6TCgTnFj8UijcBgXQpaO8cISUfiW61Iw"
heroku config:set SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZicmtkcGphcGxxcm5nYXJnaHl1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODk1MzU2NSwiZXhwIjoyMDc0NTI5NTY1fQ.EcuFAtDtYoafFznel4ZSuIeP3BYC6HyT3z_sCEnrHRg"

# Encryption Key (IMPORTANT: Generate a new one for production)
heroku config:set ENCRYPTION_KEY="your-fernet-encryption-key-here"

# Pesapal API (Platform Revenue)
heroku config:set PESAPAL_CONSUMER_KEY="c7tKYh47BTA3kqExs7OOI8ghj2emni62"
heroku config:set PESAPAL_CONSUMER_SECRET="jQcz5iYPZW121PW2kUU+o3piBO4="
heroku config:set PESAPAL_BASE_URL="https://cybqa.pesapal.com/pesapalv3/api/"
heroku config:set PESAPAL_CALLBACK_URL="https://hotspott-39e105144510.herokuapp.com/api/payments/pesapal/callback/"
heroku config:set PESAPAL_IPN_URL="https://hotspott-39e105144510.herokuapp.com/api/payments/pesapal/ipn/"

# Email Settings
heroku config:set EMAIL_HOST="smtp.gmail.com"
heroku config:set EMAIL_PORT="587"
heroku config:set EMAIL_USE_TLS="True"
heroku config:set EMAIL_HOST_USER="mainaadam277@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="cwch eysq lofx tubi"
heroku config:set DEFAULT_FROM_EMAIL="mainaadam277@gmail.com"

# Frontend URL
heroku config:set FRONTEND_URL="https://hotspott-39e105144510.herokuapp.com/"

# Additional Required Variables
heroku config:set DJANGO_SETTINGS_MODULE="hotspot_config.settings"
heroku config:set PYTHONPATH="/app"
```

## 🚀 **Deployment Commands**

After setting the environment variables, run these commands:

```bash
# 1. Deploy to Heroku
git push heroku main

# 2. Run database migrations
heroku run python manage.py migrate

# 3. Collect static files
heroku run python manage.py collectstatic --noinput

# 4. Create superuser (optional)
heroku run python manage.py createsuperuser

# 5. Open the app
heroku open
```

## ⚠️ **Important Notes**

1. **Generate a new ENCRYPTION_KEY** for production:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

2. **Test in sandbox mode first** before going live

3. **Set up Heroku Scheduler** for automation tasks

4. **Configure your first provider's M-PESA credentials** after deployment

## 🎯 **After Deployment**

1. Visit: https://hotspott-39e105144510.herokuapp.com/
2. Create a superuser account
3. Test the payment flows
4. Configure provider M-PESA credentials
5. Set up automation tasks

## 📞 **Support**

If you encounter any issues:
1. Check Heroku logs: `heroku logs --tail`
2. Verify environment variables: `heroku config`
3. Test database connection: `heroku run python manage.py dbshell`

Your MikroTik Hotspot Platform is now ready for production! 🎉

# 🚀 Heroku Deployment Steps

## 📋 Prerequisites

### 1. Install Heroku CLI
- Download from: https://devcenter.heroku.com/articles/heroku-cli
- Install and restart your terminal
- Verify installation: `heroku --version`

### 2. Set up Supabase Database
- Go to https://supabase.com
- Create a new project
- Get your database URL and API keys
- Run the SQL from `database_schema.sql` in Supabase SQL editor

### 3. Set up Pesapal Account
- Go to https://developer.pesapal.com/
- Create developer account
- Get Consumer Key and Consumer Secret
- Set up webhook URLs

## 🚀 Deployment Steps

### Step 1: Login to Heroku
```bash
heroku login
```

### Step 2: Create Heroku App
```bash
heroku create your-hotspot-ticketing-app
```

### Step 3: Add Required Addons
```bash
# PostgreSQL (if not using Supabase)
heroku addons:create heroku-postgresql:hobby-dev

# Redis for Celery
heroku addons:create heroku-redis:hobby-dev

# SendGrid for emails
heroku addons:create sendgrid:starter

# Scheduler for background jobs
heroku addons:create scheduler:standard
```

### Step 4: Set Environment Variables
```bash
# Django Settings
heroku config:set SECRET_KEY="your-super-secret-key-here"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-hotspot-ticketing-app.herokuapp.com"

# Database (Supabase)
heroku config:set DATABASE_URL="postgresql://username:password@host:port/database"
heroku config:set SUPABASE_URL="https://your-project.supabase.co"
heroku config:set SUPABASE_KEY="your-supabase-anon-key"
heroku config:set SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"

# Pesapal Settings
heroku config:set PESAPAL_CONSUMER_KEY="your-pesapal-consumer-key"
heroku config:set PESAPAL_CONSUMER_SECRET="your-pesapal-consumer-secret"
heroku config:set PESAPAL_BASE_URL="https://cybqa.pesapal.com/pesapalv3/api/"
heroku config:set PESAPAL_CALLBACK_URL="https://your-hotspot-ticketing-app.herokuapp.com/api/payments/pesapal/callback/"
heroku config:set PESAPAL_IPN_URL="https://your-hotspot-ticketing-app.herokuapp.com/api/payments/pesapal/ipn/"

# Email Settings
heroku config:set SENDGRID_API_KEY="your-sendgrid-api-key"
heroku config:set DEFAULT_FROM_EMAIL="noreply@yourdomain.com"

# Redis
heroku config:set REDIS_URL="redis://localhost:6379"

# Frontend URL
heroku config:set FRONTEND_URL="https://your-hotspot-ticketing-app.herokuapp.com"
```

### Step 5: Deploy to Heroku
```bash
git push heroku main
```

### Step 6: Run Migrations and Setup
```bash
# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Load sample data
heroku run python manage.py create_sample_ticket_types
```

### Step 7: Set up Background Jobs
In Heroku Dashboard > Scheduler, add these jobs:

1. **Daily Ticket Expiry Check** (Daily at 2:00 AM UTC):
   ```
   python manage.py shell -c "from tickets.tasks import expire_tickets; expire_tickets.delay()"
   ```

2. **Daily Cleanup** (Daily at 3:00 AM UTC):
   ```
   python manage.py shell -c "from tickets.tasks import cleanup_old_tickets; cleanup_old_tickets.delay()"
   ```

3. **Daily Reports** (Daily at 4:00 AM UTC):
   ```
   python manage.py shell -c "from tickets.tasks import generate_daily_reports; generate_daily_reports.delay()"
   ```

## 🎯 Quick Deployment Script

Run the `deploy-heroku.bat` file for automated deployment:

```bash
deploy-heroku.bat
```

## ✅ Verification

After deployment, verify:

1. **App is running**: Visit `https://your-hotspot-ticketing-app.herokuapp.com`
2. **Admin works**: Visit `https://your-hotspot-ticketing-app.herokuapp.com/admin`
3. **API works**: Test endpoints at `https://your-hotspot-ticketing-app.herokuapp.com/api/tickets/ticket-types/`
4. **Database**: Check that sample data was loaded

## 🔧 Troubleshooting

### Common Issues:

1. **Build fails**: Check `heroku logs --tail`
2. **Database errors**: Verify DATABASE_URL is correct
3. **Static files**: Ensure WhiteNoise is configured
4. **Environment variables**: Check with `heroku config`

### Useful Commands:

```bash
# View logs
heroku logs --tail

# Check config
heroku config

# Run Django shell
heroku run python manage.py shell

# Check database
heroku run python manage.py dbshell

# Restart app
heroku restart
```

## 🎉 Success!

Your MikroTik Hotspot Ticketing System is now live on Heroku! 

**Next Steps:**
1. Test all features thoroughly
2. Set up your domain (optional)
3. Configure monitoring and alerts
4. Start serving customers!

---

**Built with ❤️ for Kenyan MikroTik hotspot providers**

# MikroTik Hotspot Ticketing System - Deployment Guide

## 🚀 Complete Deployment Guide

This guide will help you deploy the MikroTik Hotspot Ticketing System to Heroku with Supabase database and Pesapal payment integration.

## 📋 Prerequisites

- Heroku CLI installed
- Git installed
- Python 3.11+ installed locally
- Supabase account
- Pesapal developer account

## 🗄️ Database Setup (Supabase)

### 1. Create Supabase Project

1. Go to [Supabase](https://supabase.com) and create a new project
2. Note down your project URL and API keys
3. Go to Settings > Database and copy your connection string

### 2. Update Database Schema

Run the following SQL in your Supabase SQL editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Run the migrations from database_schema.sql
-- (Copy the contents of database_schema.sql and run in Supabase)
```

## 💳 Payment Setup (Pesapal)

### 1. Create Pesapal Account

1. Go to [Pesapal Developer Portal](https://developer.pesapal.com/)
2. Create a developer account
3. Create a new application
4. Get your Consumer Key and Consumer Secret

### 2. Configure Webhooks

Set up the following webhook URLs in your Pesapal dashboard:
- Callback URL: `https://your-app.herokuapp.com/api/payments/pesapal/callback/`
- IPN URL: `https://your-app.herokuapp.com/api/payments/pesapal/ipn/`

## 🚀 Heroku Deployment

### 1. Create Heroku App

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-hotspot-ticketing-app

# Add PostgreSQL addon (if not using Supabase)
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis addon for Celery
heroku addons:create heroku-redis:hobby-dev

# Add SendGrid for emails
heroku addons:create sendgrid:starter
```

### 2. Set Environment Variables

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

### 3. Deploy Application

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Add Heroku remote
heroku git:remote -a your-hotspot-ticketing-app

# Deploy to Heroku
git push heroku main
```

### 4. Run Database Migrations

```bash
# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Load sample data
heroku run python manage.py create_sample_ticket_types
```

### 5. Set Up Background Jobs

```bash
# Add Heroku Scheduler addon
heroku addons:create scheduler:standard
```

Add these scheduled jobs in the Heroku dashboard:

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

## 🔧 Local Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd hotspot-billing-system

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### 2. Environment Variables

Create a `.env` file:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Supabase)
DATABASE_URL=postgresql://username:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Pesapal Settings
PESAPAL_CONSUMER_KEY=your-pesapal-consumer-key
PESAPAL_CONSUMER_SECRET=your-pesapal-consumer-secret
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3/api/
PESAPAL_CALLBACK_URL=http://localhost:8000/api/payments/pesapal/callback/
PESAPAL_IPN_URL=http://localhost:8000/api/payments/pesapal/ipn/

# Email Settings
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Redis
REDIS_URL=redis://localhost:6379

# Frontend URL
FRONTEND_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py create_sample_ticket_types

# Run development server
python manage.py runserver
```

## 📱 Features Overview

### ✅ Implemented Features

1. **Landing Page** - Marketing-focused homepage with pricing and features
2. **User Authentication** - Registration, login, and user management
3. **Ticket Management** - Create, manage, and track tickets/vouchers
4. **Ticket Types** - Time-based and data-based ticket configurations
5. **Sales Tracking** - Revenue tracking and analytics
6. **Dashboard** - User-friendly dashboard for ticket management
7. **API Endpoints** - RESTful API for all ticket operations
8. **Admin Interface** - Django admin for system management

### 🚧 Pending Features

1. **Pesapal Integration** - Payment processing with webhooks
2. **MikroTik Config Generation** - Generate .rsc files for routers
3. **Ticket Expiry Automation** - Automatic ticket expiration
4. **Printing System** - PDF generation for tickets
5. **Advanced Analytics** - Detailed reporting and charts

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### Tickets
- `GET /api/tickets/ticket-types/` - List ticket types
- `GET /api/tickets/tickets/` - List user tickets
- `POST /api/tickets/tickets/` - Create new ticket
- `GET /api/tickets/tickets/stats/` - Ticket statistics
- `POST /api/tickets/batches/` - Create ticket batch
- `GET /api/tickets/sales/` - List ticket sales

### Dashboard
- `GET /api/dashboard/stats/` - Dashboard statistics
- `GET /api/dashboard/subscription/` - Subscription status

## 🎯 Usage Guide

### For Hotspot Operators

1. **Sign Up** - Create an account on the platform
2. **Choose Plan** - Select a subscription plan
3. **Create Ticket Types** - Set up time-based or data-based tickets
4. **Generate Tickets** - Create individual tickets or batches
5. **Sell Tickets** - Track sales and revenue
6. **Monitor Usage** - View analytics and reports

### For Customers

1. **Purchase Tickets** - Buy tickets from hotspot operators
2. **Use WiFi** - Connect using ticket credentials
3. **Track Usage** - Monitor remaining time/data

## 🔒 Security Features

- **Authentication** - JWT token-based authentication
- **Authorization** - Role-based access control
- **Payment Security** - Pesapal signature verification
- **Data Protection** - Row-level security in Supabase
- **HTTPS** - Enforced SSL in production

## 📊 Monitoring

### Heroku Metrics
- Monitor app performance in Heroku dashboard
- Set up alerts for errors and performance issues
- Monitor database and Redis usage

### Application Logs
- Django logs for application errors
- Celery logs for background job status
- Payment logs for transaction tracking

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify DATABASE_URL is correct
   - Check Supabase connection settings

2. **Payment Integration Issues**
   - Verify Pesapal credentials
   - Check webhook URLs are accessible

3. **Background Jobs Not Running**
   - Verify Redis connection
   - Check Heroku Scheduler configuration

### Support

- Check application logs: `heroku logs --tail`
- Verify environment variables: `heroku config`
- Test database connection: `heroku run python manage.py dbshell`

## 🎉 Success!

Your MikroTik Hotspot Ticketing System is now deployed and ready to help hotspot operators monetize their WiFi services!

### Next Steps

1. Test the application thoroughly
2. Set up monitoring and alerts
3. Train users on the system
4. Monitor performance and usage
5. Plan for scaling as your user base grows

---

**Built with ❤️ for Kenyan MikroTik hotspot providers**

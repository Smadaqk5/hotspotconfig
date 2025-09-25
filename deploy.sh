#!/bin/bash

# MikroTik Hotspot Config Generator - Deployment Script
# This script automates the deployment process to Heroku

set -e  # Exit on any error

echo "🚀 Starting deployment to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first."
    echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run 'heroku login' first."
    exit 1
fi

# Get app name from user or use default
if [ -z "$1" ]; then
    echo "Enter your Heroku app name (or press Enter for 'mikrotik-hotspot-config'):"
    read -r APP_NAME
    APP_NAME=${APP_NAME:-mikrotik-hotspot-config}
else
    APP_NAME=$1
fi

echo "📱 Using app name: $APP_NAME"

# Create Heroku app if it doesn't exist
if ! heroku apps:info -a "$APP_NAME" &> /dev/null; then
    echo "📦 Creating Heroku app: $APP_NAME"
    heroku create "$APP_NAME"
else
    echo "✅ App $APP_NAME already exists"
fi

# Add required addons
echo "🔧 Adding required addons..."

# PostgreSQL
if ! heroku addons:info -a "$APP_NAME" | grep -q "heroku-postgresql"; then
    echo "📊 Adding PostgreSQL addon..."
    heroku addons:create heroku-postgresql:hobby-dev -a "$APP_NAME"
else
    echo "✅ PostgreSQL addon already exists"
fi

# Redis
if ! heroku addons:info -a "$APP_NAME" | grep -q "heroku-redis"; then
    echo "🔴 Adding Redis addon..."
    heroku addons:create heroku-redis:hobby-dev -a "$APP_NAME"
else
    echo "✅ Redis addon already exists"
fi

# SendGrid
if ! heroku addons:info -a "$APP_NAME" | grep -q "sendgrid"; then
    echo "📧 Adding SendGrid addon..."
    heroku addons:create sendgrid:starter -a "$APP_NAME"
else
    echo "✅ SendGrid addon already exists"
fi

# Scheduler
if ! heroku addons:info -a "$APP_NAME" | grep -q "scheduler"; then
    echo "⏰ Adding Scheduler addon..."
    heroku addons:create scheduler:standard -a "$APP_NAME"
else
    echo "✅ Scheduler addon already exists"
fi

# Set environment variables
echo "🔐 Setting environment variables..."

# Generate a secret key
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

heroku config:set -a "$APP_NAME" \
    SECRET_KEY="$SECRET_KEY" \
    DEBUG=False \
    ALLOWED_HOSTS="$APP_NAME.herokuapp.com" \
    FRONTEND_URL="https://$APP_NAME.herokuapp.com"

echo "⚠️  Please set the following environment variables manually:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_KEY"
echo "   - SUPABASE_SERVICE_ROLE_KEY"
echo "   - PESAPAL_CONSUMER_KEY"
echo "   - PESAPAL_CONSUMER_SECRET"
echo "   - PESAPAL_CALLBACK_URL=https://$APP_NAME.herokuapp.com/api/payments/pesapal/callback/"
echo "   - PESAPAL_IPN_URL=https://$APP_NAME.herokuapp.com/api/payments/pesapal/ipn/"

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku" || echo "No changes to commit"
git push heroku main

# Run migrations
echo "🗄️  Running database migrations..."
heroku run python manage.py migrate -a "$APP_NAME"

# Create superuser
echo "👤 Creating superuser..."
echo "You'll need to create a superuser manually:"
echo "heroku run python manage.py createsuperuser -a $APP_NAME"

# Load sample data
echo "📊 Loading sample data..."
heroku run python manage.py shell -a "$APP_NAME" -c "
from django.core.management import execute_from_command_line
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
from django.db import connection
with connection.cursor() as cursor:
    with open('sample_data.sql', 'r') as f:
        cursor.execute(f.read())
"

# Set up scheduled jobs
echo "⏰ Setting up scheduled jobs..."
echo "Please add the following jobs in Heroku Scheduler:"
echo "1. Daily at 00:00 UTC: python manage.py shell -c \"from subscriptions.tasks import check_expired_subscriptions; check_expired_subscriptions.delay()\""
echo "2. Daily at 09:00 UTC: python manage.py shell -c \"from subscriptions.tasks import send_renewal_reminders; send_renewal_reminders.delay()\""

echo "✅ Deployment completed!"
echo "🌐 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📊 Admin panel: https://$APP_NAME.herokuapp.com/admin/"
echo ""
echo "Next steps:"
echo "1. Set up your Supabase database and get the connection details"
echo "2. Set up your Pesapal account and get API credentials"
echo "3. Configure the environment variables in Heroku"
echo "4. Create a superuser account"
echo "5. Set up the scheduled jobs in Heroku Scheduler"
echo "6. Test the payment flow with Pesapal sandbox"

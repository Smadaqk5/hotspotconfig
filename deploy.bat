@echo off
REM MikroTik Hotspot Config Generator - Deployment Script for Windows
REM This script automates the deployment process to Heroku

echo 🚀 Starting deployment to Heroku...

REM Check if Heroku CLI is installed
heroku --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Heroku CLI is not installed. Please install it first.
    echo Visit: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Check if user is logged in to Heroku
heroku auth:whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Not logged in to Heroku. Please run 'heroku login' first.
    pause
    exit /b 1
)

REM Get app name from user or use default
if "%1"=="" (
    set /p APP_NAME="Enter your Heroku app name (or press Enter for 'mikrotik-hotspot-config'): "
    if "%APP_NAME%"=="" set APP_NAME=mikrotik-hotspot-config
) else (
    set APP_NAME=%1
)

echo 📱 Using app name: %APP_NAME%

REM Create Heroku app if it doesn't exist
heroku apps:info -a %APP_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Creating Heroku app: %APP_NAME%
    heroku create %APP_NAME%
) else (
    echo ✅ App %APP_NAME% already exists
)

REM Add required addons
echo 🔧 Adding required addons...

REM PostgreSQL
heroku addons:info -a %APP_NAME% | findstr "heroku-postgresql" >nul
if %errorlevel% neq 0 (
    echo 📊 Adding PostgreSQL addon...
    heroku addons:create heroku-postgresql:hobby-dev -a %APP_NAME%
) else (
    echo ✅ PostgreSQL addon already exists
)

REM Redis
heroku addons:info -a %APP_NAME% | findstr "heroku-redis" >nul
if %errorlevel% neq 0 (
    echo 🔴 Adding Redis addon...
    heroku addons:create heroku-redis:hobby-dev -a %APP_NAME%
) else (
    echo ✅ Redis addon already exists
)

REM SendGrid
heroku addons:info -a %APP_NAME% | findstr "sendgrid" >nul
if %errorlevel% neq 0 (
    echo 📧 Adding SendGrid addon...
    heroku addons:create sendgrid:starter -a %APP_NAME%
) else (
    echo ✅ SendGrid addon already exists
)

REM Scheduler
heroku addons:info -a %APP_NAME% | findstr "scheduler" >nul
if %errorlevel% neq 0 (
    echo ⏰ Adding Scheduler addon...
    heroku addons:create scheduler:standard -a %APP_NAME%
) else (
    echo ✅ Scheduler addon already exists
)

REM Set environment variables
echo 🔐 Setting environment variables...

REM Generate a secret key
for /f %%i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set SECRET_KEY=%%i

heroku config:set -a %APP_NAME% SECRET_KEY=%SECRET_KEY% DEBUG=False ALLOWED_HOSTS=%APP_NAME%.herokuapp.com FRONTEND_URL=https://%APP_NAME%.herokuapp.com

echo ⚠️  Please set the following environment variables manually:
echo    - SUPABASE_URL
echo    - SUPABASE_KEY
echo    - SUPABASE_SERVICE_ROLE_KEY
echo    - PESAPAL_CONSUMER_KEY
echo    - PESAPAL_CONSUMER_SECRET
echo    - PESAPAL_CALLBACK_URL=https://%APP_NAME%.herokuapp.com/api/payments/pesapal/callback/
echo    - PESAPAL_IPN_URL=https://%APP_NAME%.herokuapp.com/api/payments/pesapal/ipn/

REM Deploy to Heroku
echo 🚀 Deploying to Heroku...
git add .
git commit -m "Deploy to Heroku" 2>nul || echo No changes to commit
git push heroku main

REM Run migrations
echo 🗄️  Running database migrations...
heroku run python manage.py migrate -a %APP_NAME%

REM Create superuser
echo 👤 Creating superuser...
echo You'll need to create a superuser manually:
echo heroku run python manage.py createsuperuser -a %APP_NAME%

echo ✅ Deployment completed!
echo 🌐 Your app is available at: https://%APP_NAME%.herokuapp.com
echo 📊 Admin panel: https://%APP_NAME%.herokuapp.com/admin/
echo.
echo Next steps:
echo 1. Set up your Supabase database and get the connection details
echo 2. Set up your Pesapal account and get API credentials
echo 3. Configure the environment variables in Heroku
echo 4. Create a superuser account
echo 5. Set up the scheduled jobs in Heroku Scheduler
echo 6. Test the payment flow with Pesapal sandbox

pause

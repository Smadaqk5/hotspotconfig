@echo off
echo 🚀 Deploying MikroTik Hotspot Ticketing System to Heroku...
echo.

echo 📋 Prerequisites:
echo 1. Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
echo 2. Login to Heroku: heroku login
echo 3. Set up Supabase database
echo 4. Get Pesapal API credentials
echo.

echo 🔧 Setting up Heroku app...
heroku create your-hotspot-ticketing-app

echo 📦 Skipping add-ons (using external services instead)...
echo Using external PostgreSQL database (Supabase)
echo Using external Redis service (optional)
echo Using external email service (SendGrid API)
echo Using external task scheduler (optional)

echo ⚙️ Setting environment variables...
echo Please update these with your actual values:

echo.
echo 🔑 Required Environment Variables:
echo SECRET_KEY=your-super-secret-key-here
echo DEBUG=False
echo ALLOWED_HOSTS=your-hotspot-ticketing-app.herokuapp.com
echo.
echo 📊 Database Configuration (Supabase):
echo DATABASE_URL=postgresql://postgres.abcdefghijklmnop:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
echo SUPABASE_URL=https://abcdefghijklmnop.supabase.co
echo SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-anon-key
echo SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-service-role-key
echo.
echo 💳 Payment Configuration:
echo PESAPAL_CONSUMER_KEY=your-pesapal-consumer-key
echo PESAPAL_CONSUMER_SECRET=your-pesapal-consumer-secret
echo PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3/api/
echo PESAPAL_CALLBACK_URL=https://your-hotspot-ticketing-app.herokuapp.com/api/payments/pesapal/callback/
echo PESAPAL_IPN_URL=https://your-hotspot-ticketing-app.herokuapp.com/api/payments/pesapal/ipn/
echo.
echo 📧 Gmail SMTP Configuration:
echo EMAIL_HOST=smtp.gmail.com
echo EMAIL_PORT=587
echo EMAIL_USE_TLS=True
echo EMAIL_HOST_USER=your-gmail@gmail.com
echo EMAIL_HOST_PASSWORD=your-gmail-app-password
echo DEFAULT_FROM_EMAIL=your-gmail@gmail.com
echo.
echo 📝 Gmail Setup Instructions:
echo 1. Enable 2-Factor Authentication on your Gmail account
echo 2. Go to Google Account Settings ^> Security ^> App passwords
echo 3. Generate a new app password for "Mail"
echo 4. Use the generated app password (not your regular password)
echo 5. Set EMAIL_HOST_USER to your Gmail address
echo 6. Set EMAIL_HOST_PASSWORD to the generated app password
echo.
echo 📝 Supabase Database Setup Instructions:
echo 1. Go to https://supabase.com/dashboard
echo 2. Create a new project
echo 3. Go to Settings ^> Database
echo 4. Copy the "Connection string" under "Connection pooling"
echo 5. Use the pooled connection string as your DATABASE_URL
echo 6. Go to Settings ^> API to get your API keys
echo.
echo 🔄 Optional Services:
echo REDIS_URL=redis://your-redis-provider.com:6379
echo FRONTEND_URL=https://your-hotspot-ticketing-app.herokuapp.com

echo.
echo 🚀 Deploying to Heroku...
git push heroku main

echo.
echo 🗄️ Setting up database...
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py create_sample_ticket_types

echo.
echo ✅ Deployment complete!
echo 🌐 Your app is available at: https://your-hotspot-ticketing-app.herokuapp.com
echo.
echo 📋 Next steps:
echo 1. Set up external services:
echo    - Supabase database (free tier available)
echo    - Gmail account with 2FA enabled
echo    - Optional: Redis provider (Redis Cloud, etc.)
echo 2. Configure Gmail app password (see instructions above)
echo 3. Configure scheduled tasks (use external cron service or Heroku Scheduler)
echo 4. Configure your domain (optional)
echo 5. Test all features
echo 6. Start serving customers!
echo.
pause

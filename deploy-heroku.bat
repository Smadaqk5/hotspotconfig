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

echo 📦 Adding required addons...
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
heroku addons:create sendgrid:starter
heroku addons:create scheduler:standard

echo ⚙️ Setting environment variables...
echo Please update these with your actual values:

echo.
echo 🔑 Required Environment Variables:
echo SECRET_KEY=your-super-secret-key-here
echo DEBUG=False
echo ALLOWED_HOSTS=your-hotspot-ticketing-app.herokuapp.com
echo DATABASE_URL=postgresql://username:password@host:port/database
echo SUPABASE_URL=https://your-project.supabase.co
echo SUPABASE_KEY=your-supabase-anon-key
echo SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
echo PESAPAL_CONSUMER_KEY=your-pesapal-consumer-key
echo PESAPAL_CONSUMER_SECRET=your-pesapal-consumer-secret
echo PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3/api/
echo PESAPAL_CALLBACK_URL=https://your-hotspot-ticketing-app.herokuapp.com/api/payments/pesapal/callback/
echo PESAPAL_IPN_URL=https://your-hotspot-ticketing-app.herokuapp.com/api/payments/pesapal/ipn/
echo SENDGRID_API_KEY=your-sendgrid-api-key
echo DEFAULT_FROM_EMAIL=noreply@yourdomain.com
echo REDIS_URL=redis://localhost:6379
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
echo 1. Set up scheduled jobs in Heroku Scheduler
echo 2. Configure your domain (optional)
echo 3. Test all features
echo 4. Start serving customers!
echo.
pause

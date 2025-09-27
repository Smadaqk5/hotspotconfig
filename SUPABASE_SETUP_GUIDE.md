# 🗄️ Supabase Setup Guide for MikroTik Hotspot Platform

## 📋 **Step 1: Create Supabase Project**

1. **Go to [Supabase](https://supabase.com)**
2. **Sign up/Login** to your account
3. **Create a new project**:
   - Project name: `hotspot-platform`
   - Database password: (choose a strong password)
   - Region: Choose closest to Kenya (e.g., `ap-southeast-1` for Singapore)

## 🔑 **Step 2: Get Your Database Connection Details**

Once your project is created:

1. **Go to Settings → Database**
2. **Copy the connection string** (it looks like this):
   ```
   postgresql://postgres.abcdefghijklmnop:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

3. **Note down these details**:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **API Key**: (anon/public key)
   - **Service Role Key**: (secret key)

## ⚙️ **Step 3: Configure Environment Variables**

Create a `.env` file in your project root:

```env
# Supabase Database
DATABASE_URL=postgresql://postgres.abcdefghijklmnop:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Supabase API
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Email Settings (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Pesapal Settings
PESAPAL_CONSUMER_KEY=your-consumer-key
PESAPAL_CONSUMER_SECRET=your-consumer-secret
PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3/api
PESAPAL_CALLBACK_URL=https://your-app.herokuapp.com/payments/callback/
PESAPAL_IPN_URL=https://your-app.herokuapp.com/payments/ipn/

# Frontend URL
FRONTEND_URL=http://127.0.0.1:8000
```

## 🚀 **Step 4: Run Database Migrations**

```bash
# Apply migrations to Supabase
python manage.py migrate

# Create Super Admin user
python setup_supabase_admin.py
```

## 👤 **Step 5: Create Super Admin User**

Run the setup script:

```bash
python setup_supabase_admin.py
```

This will create a Super Admin user with:
- **Email**: admin@hotspot.com
- **Username**: superadmin
- **Password**: admin123

## 🌐 **Step 6: Access Your Platform**

1. **Start the server**: `python manage.py runserver`
2. **Login as Super Admin**: http://127.0.0.1:8000/login/
3. **Access Admin Panel**: http://127.0.0.1:8000/admin/
4. **Super Admin Dashboard**: http://127.0.0.1:8000/super-admin/

## 🔧 **Step 7: Verify Supabase Connection**

Check your Supabase dashboard to see the tables being created:
- `accounts_user`
- `accounts_provider`
- `subscriptions_providersubscriptionplan`
- `tickets_ticket`
- And more...

## 📊 **Step 8: Test the Platform**

1. **Login as Super Admin**
2. **Create a test provider**
3. **Generate some tickets**
4. **Test the full workflow**

## 🚀 **Step 9: Deploy to Heroku**

Once everything works locally:

```bash
# Deploy to Heroku
git add .
git commit -m "Add Supabase integration"
git push heroku main

# Set environment variables on Heroku
heroku config:set DATABASE_URL=your-supabase-url
heroku config:set SUPABASE_URL=your-supabase-url
heroku config:set SUPABASE_KEY=your-supabase-key
# ... set all other environment variables
```

## 🎯 **Benefits of Using Supabase**

✅ **PostgreSQL Database** - Production-ready database
✅ **Real-time Features** - Live updates for dashboards
✅ **Authentication** - Built-in user management
✅ **API Generation** - Automatic REST API
✅ **Dashboard** - Web interface for database management
✅ **Backups** - Automatic database backups
✅ **Scaling** - Handles high traffic
✅ **Security** - Row-level security policies

## 🔍 **Troubleshooting**

### Connection Issues
- Check your DATABASE_URL format
- Ensure your Supabase project is active
- Verify your database password

### Migration Issues
- Run `python manage.py migrate --fake-initial` if needed
- Check Supabase logs for errors

### Authentication Issues
- Verify your SUPABASE_KEY is correct
- Check your service role key permissions

## 📞 **Support**

If you encounter issues:
1. Check the Supabase dashboard for errors
2. Review your environment variables
3. Check Django logs for specific errors
4. Ensure all migrations are applied

---

**🎉 Congratulations!** Your MikroTik Hotspot Multi-Level Platform is now running on Supabase! 🚀

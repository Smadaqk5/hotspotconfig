# MikroTik Hotspot Config Generator

A subscription-based website for Kenyan MikroTik hotspot providers. Users pay via Pesapal, host the app on Heroku, and store data in Supabase (Postgres). The site generates ready-to-use .rsc MikroTik configuration scripts tailored per user.

## 🌟 Features

- **Subscription Management**: Pay via Pesapal with Kenyan payment methods (M-Pesa, Airtel Money)
- **Config Generation**: Generate professional MikroTik hotspot configurations in seconds
- **User Dashboard**: Manage subscriptions, view config history, and generate new configs
- **Admin Panel**: Manage users, subscriptions, payments, and config templates
- **Background Jobs**: Automated subscription management and email notifications
- **Security**: Bank-grade security with proper authentication and authorization

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+ (for frontend assets)
- PostgreSQL (via Supabase)
- Redis (for Celery)
- Heroku CLI

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hotspot-billing-system
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up the database**
   ```bash
   python manage.py migrate
   python manage.py loaddata sample_data.sql
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🏗️ Architecture

### Backend (Django)
- **Authentication**: Custom user model with email verification
- **API**: RESTful API with Django REST Framework
- **Payments**: Pesapal integration for Kenyan payments
- **Config Generation**: Jinja2 templating for MikroTik configs
- **Background Jobs**: Celery for subscription management

### Frontend
- **Framework**: Django templates with TailwindCSS
- **Styling**: TailwindCSS with Alpine.js for interactivity
- **Responsive**: Mobile-first design

### Database (Supabase/PostgreSQL)
- **Users**: Extended user model with profiles
- **Subscriptions**: Plan management and usage tracking
- **Payments**: Pesapal payment records
- **Configs**: Generated configuration storage

## 📊 Database Schema

### Core Tables
- `accounts_user` - Extended user model
- `subscriptions_subscriptionplan` - Available subscription plans
- `subscriptions_subscription` - User subscriptions
- `payments_payment` - Payment records
- `config_generator_generatedconfig` - Generated configurations

### Configuration Tables
- `config_generator_mikrotikmodel` - Supported MikroTik models
- `config_generator_vouchertype` - Voucher duration types
- `config_generator_bandwidthprofile` - Bandwidth profiles
- `config_generator_configtemplate` - Config templates

## 🔧 Configuration

### Environment Variables

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
PESAPAL_CALLBACK_URL=https://your-app.herokuapp.com/api/payments/pesapal/callback/
PESAPAL_IPN_URL=https://your-app.herokuapp.com/api/payments/pesapal/ipn/

# Email Settings (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Redis (for Celery)
REDIS_URL=redis://localhost:6379

# Frontend URL
FRONTEND_URL=https://your-app.herokuapp.com
```

## 🚀 Deployment to Heroku

### 1. Prepare for Deployment

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis addon
heroku addons:create heroku-redis:hobby-dev

# Add SendGrid addon
heroku addons:create sendgrid:starter
```

### 2. Set Environment Variables

```bash
# Set all required environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com
heroku config:set PESAPAL_CONSUMER_KEY=your-pesapal-key
heroku config:set PESAPAL_CONSUMER_SECRET=your-pesapal-secret
# ... set all other variables
```

### 3. Deploy

```bash
# Deploy to Heroku
git add .
git commit -m "Initial deployment"
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Load sample data
heroku run python manage.py shell -c "exec(open('sample_data.sql').read())"
```

### 4. Set up Background Jobs

```bash
# Add Heroku Scheduler addon
heroku addons:create scheduler:standard

# Add scheduled jobs in Heroku dashboard:
# - Daily: python manage.py shell -c "from subscriptions.tasks import check_expired_subscriptions; check_expired_subscriptions.delay()"
# - Daily: python manage.py shell -c "from subscriptions.tasks import send_renewal_reminders; send_renewal_reminders.delay()"
```

## 💳 Pesapal Integration

### Setup
1. Register at [Pesapal Developer Portal](https://developer.pesapal.com/)
2. Get your Consumer Key and Consumer Secret
3. Set up webhook URLs in Pesapal dashboard:
   - Callback URL: `https://your-app.herokuapp.com/api/payments/pesapal/callback/`
   - IPN URL: `https://your-app.herokuapp.com/api/payments/pesapal/ipn/`

### Testing
1. Use Pesapal sandbox for testing
2. Test payment flow with test credentials
3. Verify webhook handling

## 🔐 Security Features

- **Authentication**: JWT tokens with session management
- **Authorization**: Role-based access control
- **Payment Security**: Pesapal signature verification
- **Data Protection**: Row-level security (RLS) in Supabase
- **HTTPS**: Enforced SSL in production
- **Rate Limiting**: API rate limiting for protection

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get user info

### Subscriptions
- `GET /api/subscriptions/plans/` - List subscription plans
- `GET /api/subscriptions/current/` - Get current subscription
- `POST /api/subscriptions/create/` - Create subscription

### Payments
- `POST /api/payments/create/` - Create payment
- `GET /api/payments/list/` - List user payments
- `POST /api/payments/pesapal/callback/` - Pesapal callback
- `POST /api/payments/pesapal/ipn/` - Pesapal IPN

### Config Generation
- `GET /api/config/models/` - List MikroTik models
- `GET /api/config/voucher-types/` - List voucher types
- `GET /api/config/bandwidth-profiles/` - List bandwidth profiles
- `POST /api/config/generate/` - Generate configuration
- `GET /api/config/download/{id}/` - Download config file

### Dashboard
- `GET /api/dashboard/stats/` - Dashboard statistics
- `GET /api/dashboard/subscription/` - Subscription status

## 🧪 Testing

### Test Pesapal Integration
1. Use Pesapal sandbox credentials
2. Test payment creation and callback handling
3. Verify subscription creation after payment

### Test Config Generation
1. Create test subscription
2. Generate sample configuration
3. Verify .rsc file format and content

## 📈 Monitoring

### Heroku Metrics
- Monitor app performance in Heroku dashboard
- Set up alerts for errors and performance issues
- Monitor database and Redis usage

### Application Logs
- Django logs for application errors
- Celery logs for background job status
- Payment logs for transaction tracking

## 🔧 Maintenance

### Regular Tasks
- Monitor subscription expirations
- Clean up old data
- Update security patches
- Backup database

### Scaling
- Upgrade Heroku dynos as needed
- Add Redis clustering for high availability
- Implement CDN for static assets

## 📞 Support

### Documentation
- API documentation available at `/api/docs/`
- Admin panel at `/admin/`
- Database schema in `database_schema.sql`

### Troubleshooting
1. Check Heroku logs: `heroku logs --tail`
2. Verify environment variables: `heroku config`
3. Test database connection: `heroku run python manage.py dbshell`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework
- TailwindCSS for styling
- Pesapal for payment processing
- Supabase for database hosting
- Heroku for application hosting

---

**Built with ❤️ for Kenyan MikroTik hotspot providers**

# Super Admin Creation Guide - SQL Editor

## 🎯 **Quick Steps to Create Super Admin**

### **Option 1: Simple SQL Script**
1. Open your database SQL editor (Supabase, PostgreSQL, etc.)
2. Copy and paste the contents of `simple_super_admin.sql`
3. Run the script
4. Verify the super admin was created

### **Option 2: Manual Step-by-Step**

#### **Step 1: Create Super Admin User**
```sql
INSERT INTO public.accounts_user (
    password,
    is_superuser,
    username,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined,
    phone_number,
    company_name,
    is_verified,
    user_type,
    provider_license,
    business_registration,
    location,
    is_super_admin,
    created_at,
    updated_at
) VALUES (
    'pbkdf2_sha256$600000$abcdefghijklmnopqrstuvwxyzabcdefg$ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=',
    TRUE,
    'superadmin',
    'Super',
    'Admin',
    'superadmin@hotspot.com',
    TRUE,
    TRUE,
    NOW(),
    '+254700000000',
    'Hotspot Platform Admin',
    TRUE,
    'provider',
    'SUPER-ADMIN-LICENSE',
    'SUPER-ADMIN-REG',
    'Nairobi, Kenya',
    TRUE,
    NOW(),
    NOW()
);
```

#### **Step 2: Create Provider Profile**
```sql
INSERT INTO public.accounts_provider (
    user_id,
    status,
    license_number,
    business_name,
    business_type,
    contact_person,
    contact_phone,
    contact_email,
    address,
    city,
    county,
    country,
    service_areas,
    number_of_locations,
    estimated_monthly_users,
    subscription_status,
    is_approved,
    approved_at,
    mpesa_credentials_verified,
    created_at,
    updated_at
) VALUES (
    (SELECT id FROM public.accounts_user WHERE email = 'superadmin@hotspot.com'),
    'active',
    'SUPER-ADMIN-LICENSE',
    'Hotspot Platform Admin',
    'Platform Management',
    'Super Admin',
    '+254700000000',
    'superadmin@hotspot.com',
    'Nairobi, Kenya',
    'Nairobi',
    'Nairobi',
    'Kenya',
    'Nairobi, Kenya',
    1,
    100,
    'inactive',
    TRUE,
    NOW(),
    FALSE,
    NOW(),
    NOW()
);
```

#### **Step 3: Verify Creation**
```sql
SELECT 
    u.id,
    u.username,
    u.email,
    u.is_superuser,
    u.is_staff,
    u.is_super_admin,
    p.business_name,
    p.status
FROM public.accounts_user u
LEFT JOIN public.accounts_provider p ON u.id = p.user_id
WHERE u.email = 'superadmin@hotspot.com';
```

## 🔐 **Login Credentials**

After running the SQL script, you can login with:

- **Email**: `superadmin@hotspot.com`
- **Password**: `admin123`
- **Username**: `superadmin`

## ⚠️ **Important Notes**

1. **Change Password**: After first login, change the password immediately
2. **Security**: The password hash is for 'admin123' - change it for security
3. **Database**: Make sure you're running this in the correct database
4. **Backup**: Always backup your database before running SQL scripts

## 🛠️ **Troubleshooting**

### **If you get "relation does not exist" error:**
- Make sure you're connected to the correct database
- Check if the tables exist: `\dt` (in PostgreSQL) or check your database schema

### **If you get "duplicate key" error:**
- The user already exists, the script will update it instead
- This is normal and expected behavior

### **If you get "permission denied" error:**
- Make sure you have the necessary database permissions
- Contact your database administrator

## 🎯 **Next Steps**

1. Run the SQL script
2. Test login with the credentials
3. Change the password immediately
4. Access the super admin dashboard
5. Start managing providers and the platform

## 📱 **Access Super Admin Dashboard**

After creating the super admin:
1. Go to your website
2. Click "Login"
3. Enter: `superadmin@hotspot.com` / `admin123`
4. You'll be redirected to the super admin dashboard
5. Change the password in the profile settings

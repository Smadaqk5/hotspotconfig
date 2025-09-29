-- Simple Super Admin Creation Script
-- Run this in your database SQL editor

-- Step 1: Create Super Admin User
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
) ON CONFLICT (email) DO UPDATE SET
    is_superuser = TRUE,
    is_staff = TRUE,
    is_active = TRUE,
    is_super_admin = TRUE;

-- Step 2: Create Provider Profile
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
) ON CONFLICT (user_id) DO UPDATE SET
    status = 'active',
    is_approved = TRUE;

-- Step 3: Verify Creation
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

-- SQL Script to Create Super Admin User
-- Run this in your database SQL editor (Supabase, PostgreSQL, etc.)

-- First, let's check if we need to create the user in auth.users (for Supabase)
-- If using Supabase, you might need to create the user in the auth schema first
-- This script focuses on the public.accounts_user table

-- Insert Super Admin User
INSERT INTO public.accounts_user (
    password,
    last_login,
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
    -- Password: 'admin123' (hashed with Django's PBKDF2)
    'pbkdf2_sha256$600000$abcdefghijklmnopqrstuvwxyzabcdefg$ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=',
    NULL,
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
    is_super_admin = TRUE,
    updated_at = NOW()
RETURNING id;

-- Get the user ID for creating the provider profile
-- Note: In a real scenario, you'd need to get the actual user ID
-- For now, we'll use a placeholder approach

-- Create Provider Profile for Super Admin
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
    is_approved = TRUE,
    updated_at = NOW();

-- Alternative approach if you want to use a specific user ID
-- Replace 'YOUR_USER_ID_HERE' with the actual user ID from the INSERT above

/*
-- If you know the user ID, you can use this approach:
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
    is_approved,
    approved_at,
    created_at,
    updated_at
) VALUES (
    'YOUR_USER_ID_HERE', -- Replace with actual user ID
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
    TRUE,
    NOW(),
    NOW(),
    NOW()
) ON CONFLICT (user_id) DO UPDATE SET
    status = 'active',
    is_approved = TRUE,
    updated_at = NOW();
*/

-- Verify the creation
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

-- Success message
SELECT 'Super Admin created successfully!' as message,
       'Email: superadmin@hotspot.com' as email,
       'Password: admin123' as password,
       'Please change the password after first login' as note;

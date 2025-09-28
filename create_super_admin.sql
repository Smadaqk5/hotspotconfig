-- Create Super Admin User in Supabase
-- Run this script in the Supabase SQL Editor

-- First, let's check if the accounts_user table exists and see its structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'accounts_user' 
ORDER BY ordinal_position;

-- Create a super admin user
-- Note: Replace 'admin@hotspotplatform.com' and 'SuperAdmin123!' with your desired credentials

INSERT INTO accounts_user (
    username,
    email,
    password,
    first_name,
    last_name,
    phone_number,
    company_name,
    is_verified,
    user_type,
    provider_license,
    business_registration,
    location,
    is_super_admin,
    is_staff,
    is_superuser,
    is_active,
    created_at,
    updated_at
) VALUES (
    'superadmin',
    'admin@hotspotplatform.com',
    'pbkdf2_sha256$600000$dummy$dummy', -- This will be replaced by Django's password hashing
    'Super',
    'Admin',
    '+254700000000',
    'Hotspot Platform',
    true,
    'end_user', -- user_type doesn't matter for super admin
    'SUPER-ADMIN-LICENSE',
    'SUPER-ADMIN-REG',
    'Nairobi, Kenya',
    true,  -- is_super_admin
    true,  -- is_staff
    true,  -- is_superuser
    true,  -- is_active
    NOW(),
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    is_super_admin = true,
    is_staff = true,
    is_superuser = true,
    is_active = true,
    updated_at = NOW();

-- Verify the super admin was created
SELECT 
    id,
    username,
    email,
    first_name,
    last_name,
    is_super_admin,
    is_staff,
    is_superuser,
    is_active,
    created_at
FROM accounts_user 
WHERE email = 'admin@hotspotplatform.com';

-- Optional: Create a Provider record for the super admin (if needed)
INSERT INTO accounts_provider (
    user_id,
    business_name,
    business_type,
    contact_person,
    contact_phone,
    contact_email,
    address,
    city,
    county,
    country,
    status,
    is_approved,
    approved_at,
    created_at,
    updated_at
) VALUES (
    (SELECT id FROM accounts_user WHERE email = 'admin@hotspotplatform.com'),
    'Super Admin Provider',
    'Platform Admin',
    'Super Admin',
    '+254700000000',
    'admin@hotspotplatform.com',
    'Nairobi, Kenya',
    'Nairobi',
    'Nairobi',
    'Kenya',
    'active',
    true,
    NOW(),
    NOW(),
    NOW()
) ON CONFLICT (user_id) DO NOTHING;

-- Show the final result
SELECT 
    u.id,
    u.username,
    u.email,
    u.is_super_admin,
    u.is_staff,
    u.is_superuser,
    p.business_name,
    p.status as provider_status
FROM accounts_user u
LEFT JOIN accounts_provider p ON u.id = p.user_id
WHERE u.email = 'admin@hotspotplatform.com';

-- Fix missing User model fields
-- This script adds all missing columns to accounts_user table

-- Add user_type field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'accounts_user' AND column_name = 'user_type') THEN
        ALTER TABLE accounts_user ADD COLUMN user_type VARCHAR(20) DEFAULT 'end_user';
    END IF;
END $$;

-- Add provider_license field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'accounts_user' AND column_name = 'provider_license') THEN
        ALTER TABLE accounts_user ADD COLUMN provider_license VARCHAR(100);
    END IF;
END $$;

-- Add business_registration field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'accounts_user' AND column_name = 'business_registration') THEN
        ALTER TABLE accounts_user ADD COLUMN business_registration VARCHAR(100);
    END IF;
END $$;

-- Add location field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'accounts_user' AND column_name = 'location') THEN
        ALTER TABLE accounts_user ADD COLUMN location VARCHAR(200);
    END IF;
END $$;

-- Add is_super_admin field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'accounts_user' AND column_name = 'is_super_admin') THEN
        ALTER TABLE accounts_user ADD COLUMN is_super_admin BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Add created_at field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'accounts_user' AND column_name = 'created_at') THEN
        ALTER TABLE accounts_user ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;

-- Add updated_at field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'accounts_user' AND column_name = 'updated_at') THEN
        ALTER TABLE accounts_user ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;
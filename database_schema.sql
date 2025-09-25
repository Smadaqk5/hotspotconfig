-- MikroTik Hotspot Config Generator Database Schema
-- This file contains the complete database schema for the application

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Django's built-in User model)
CREATE TABLE IF NOT EXISTS accounts_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) UNIQUE NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    phone_number VARCHAR(15),
    company_name VARCHAR(100),
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- User profiles table
CREATE TABLE IF NOT EXISTS accounts_userprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    bio TEXT,
    location VARCHAR(100),
    website VARCHAR(200),
    avatar VARCHAR(100),
    UNIQUE(user_id)
);

-- Subscription plans table
CREATE TABLE IF NOT EXISTS subscriptions_subscriptionplan (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    duration_days INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    features JSONB DEFAULT '[]'::jsonb
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions_subscription (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES subscriptions_subscriptionplan(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('active', 'expired', 'cancelled', 'pending')),
    start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    auto_renew BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Subscription usage tracking
CREATE TABLE IF NOT EXISTS subscriptions_subscriptionusage (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions_subscription(id) ON DELETE CASCADE,
    configs_generated INTEGER NOT NULL DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments_payment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'KES',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    payment_method VARCHAR(20) NOT NULL DEFAULT 'pesapal' CHECK (payment_method IN ('pesapal', 'manual')),
    pesapal_order_tracking_id VARCHAR(100),
    pesapal_merchant_reference VARCHAR(100),
    pesapal_payment_reference VARCHAR(100),
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Payment items table
CREATE TABLE IF NOT EXISTS payments_paymentitem (
    id SERIAL PRIMARY KEY,
    payment_id UUID NOT NULL REFERENCES payments_payment(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);

-- MikroTik models table
CREATE TABLE IF NOT EXISTS config_generator_mikrotikmodel (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Voucher types table
CREATE TABLE IF NOT EXISTS config_generator_vouchertype (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    duration_hours INTEGER NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Bandwidth profiles table
CREATE TABLE IF NOT EXISTS config_generator_bandwidthprofile (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    download_speed VARCHAR(20) NOT NULL,
    upload_speed VARCHAR(20) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Config templates table
CREATE TABLE IF NOT EXISTS config_generator_configtemplate (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    mikrotik_model_id INTEGER NOT NULL REFERENCES config_generator_mikrotikmodel(id) ON DELETE CASCADE,
    template_content TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Generated configs table
CREATE TABLE IF NOT EXISTS config_generator_generatedconfig (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    template_id INTEGER NOT NULL REFERENCES config_generator_configtemplate(id) ON DELETE CASCADE,
    config_name VARCHAR(200) NOT NULL,
    config_content TEXT NOT NULL,
    hotspot_name VARCHAR(100) NOT NULL,
    hotspot_ip INET NOT NULL,
    dns_servers VARCHAR(200) NOT NULL,
    voucher_type_id INTEGER NOT NULL REFERENCES config_generator_vouchertype(id) ON DELETE CASCADE,
    bandwidth_profile_id INTEGER NOT NULL REFERENCES config_generator_bandwidthprofile(id) ON DELETE CASCADE,
    max_users INTEGER NOT NULL DEFAULT 50,
    voucher_length INTEGER NOT NULL DEFAULT 8,
    voucher_prefix VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions_subscription(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions_subscription(status);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments_payment(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments_payment(status);
CREATE INDEX IF NOT EXISTS idx_generated_configs_user_id ON config_generator_generatedconfig(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_configs_created_at ON config_generator_generatedconfig(created_at);

-- Row Level Security (RLS) policies for Supabase
ALTER TABLE accounts_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts_userprofile ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions_subscription ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments_payment ENABLE ROW LEVEL SECURITY;
ALTER TABLE config_generator_generatedconfig ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own profile" ON accounts_user FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON accounts_user FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own subscriptions" ON subscriptions_subscription FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view own payments" ON payments_payment FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view own generated configs" ON config_generator_generatedconfig FOR SELECT USING (auth.uid() = user_id);

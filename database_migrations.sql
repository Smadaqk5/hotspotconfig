-- Database Migration: Updated Payment Flows
-- Run this SQL on your Supabase/PostgreSQL database

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Add new fields to providers table
ALTER TABLE accounts_provider 
ADD COLUMN IF NOT EXISTS pesapal_merchant_id TEXT,
ADD COLUMN IF NOT EXISTS mpesa_consumer_key TEXT,      -- encrypted
ADD COLUMN IF NOT EXISTS mpesa_consumer_secret TEXT,    -- encrypted  
ADD COLUMN IF NOT EXISTS mpesa_shortcode TEXT,
ADD COLUMN IF NOT EXISTS mpesa_passkey TEXT,           -- encrypted
ADD COLUMN IF NOT EXISTS mpesa_callback_path TEXT,     -- /api/mpesa/callback/{provider_id}
ADD COLUMN IF NOT EXISTS mpesa_environment VARCHAR(10) DEFAULT 'sandbox';

-- Create provider subscriptions table
CREATE TABLE IF NOT EXISTS provider_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id BIGINT REFERENCES accounts_provider(id) ON DELETE CASCADE,
    plan_id BIGINT, -- references subscription plan
    status VARCHAR(20) DEFAULT 'pending', -- 'active','expired','pending','failed'
    start_date TIMESTAMPTZ,
    expiry_date TIMESTAMPTZ,
    activated_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    order_id VARCHAR(100) UNIQUE,
    amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'KES',
    payment_method VARCHAR(50) DEFAULT 'pesapal',
    payment_reference VARCHAR(100),
    ipn_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create unified payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id BIGINT REFERENCES accounts_provider(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'pesapal_provider_subscription' | 'mpesa_customer_payment'
    provider_payload JSONB, -- raw webhook data for auditing
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KES',
    external_txn_id VARCHAR(100), -- pesapal or mpesa transaction id
    status VARCHAR(20) DEFAULT 'pending', -- 'pending','success','failed'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create tickets table for WiFi vouchers
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id BIGINT REFERENCES accounts_provider(id) ON DELETE CASCADE,
    code VARCHAR(20) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    plan_type VARCHAR(10) DEFAULT 'time', -- 'time' or 'data'
    duration_hours INTEGER,
    data_limit_mb INTEGER,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KES',
    status VARCHAR(20) DEFAULT 'active', -- 'active','used','expired','cancelled'
    expires_at TIMESTAMPTZ,
    used_at TIMESTAMPTZ,
    device_mac VARCHAR(17),
    device_ip INET,
    session_start TIMESTAMPTZ,
    session_end TIMESTAMPTZ,
    data_used_mb INTEGER DEFAULT 0,
    payment_id UUID REFERENCES payments(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create ticket types table
CREATE TABLE IF NOT EXISTS ticket_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id BIGINT REFERENCES accounts_provider(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) DEFAULT 'time', -- 'time' or 'data'
    duration_hours INTEGER,
    data_limit_mb INTEGER,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KES',
    download_speed_mbps INTEGER DEFAULT 5,
    upload_speed_mbps INTEGER DEFAULT 2,
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'fas fa-wifi',
    color VARCHAR(7) DEFAULT '#3B82F6',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create ticket usage tracking table
CREATE TABLE IF NOT EXISTS ticket_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    session_start TIMESTAMPTZ NOT NULL,
    session_end TIMESTAMPTZ,
    device_mac VARCHAR(17) NOT NULL,
    device_ip INET NOT NULL,
    data_used_mb INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_provider_subscriptions_provider_status 
ON provider_subscriptions(provider_id, status);

CREATE INDEX IF NOT EXISTS idx_payments_provider_type_status 
ON payments(provider_id, type, status);

CREATE INDEX IF NOT EXISTS idx_payments_external_txn_id 
ON payments(external_txn_id);

CREATE INDEX IF NOT EXISTS idx_tickets_provider_status 
ON tickets(provider_id, status);

CREATE INDEX IF NOT EXISTS idx_tickets_code 
ON tickets(code);

CREATE INDEX IF NOT EXISTS idx_tickets_expires_at 
ON tickets(expires_at);

CREATE INDEX IF NOT EXISTS idx_ticket_types_provider_active 
ON ticket_types(provider_id, is_active);

-- Add foreign key constraints
ALTER TABLE payments 
ADD CONSTRAINT fk_payments_provider 
FOREIGN KEY (provider_id) REFERENCES accounts_provider(id) ON DELETE CASCADE;

ALTER TABLE tickets 
ADD CONSTRAINT fk_tickets_provider 
FOREIGN KEY (provider_id) REFERENCES accounts_provider(id) ON DELETE CASCADE;

ALTER TABLE tickets 
ADD CONSTRAINT fk_tickets_payment 
FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE SET NULL;

ALTER TABLE ticket_types 
ADD CONSTRAINT fk_ticket_types_provider 
FOREIGN KEY (provider_id) REFERENCES accounts_provider(id) ON DELETE CASCADE;

ALTER TABLE ticket_usage 
ADD CONSTRAINT fk_ticket_usage_ticket 
FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE;

-- Add Row Level Security (RLS)
ALTER TABLE provider_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_usage ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for provider isolation
CREATE POLICY provider_subscriptions_policy ON provider_subscriptions
    FOR ALL TO authenticated
    USING (provider_id = auth.uid() OR auth.role() = 'super_admin');

CREATE POLICY payments_policy ON payments
    FOR ALL TO authenticated
    USING (provider_id = auth.uid() OR auth.role() = 'super_admin');

CREATE POLICY tickets_policy ON tickets
    FOR ALL TO authenticated
    USING (provider_id = auth.uid() OR auth.role() = 'super_admin');

CREATE POLICY ticket_types_policy ON ticket_types
    FOR ALL TO authenticated
    USING (provider_id = auth.uid() OR auth.role() = 'super_admin');

CREATE POLICY ticket_usage_policy ON ticket_usage
    FOR ALL TO authenticated
    USING (ticket_id IN (
        SELECT id FROM tickets WHERE provider_id = auth.uid()
    ) OR auth.role() = 'super_admin');

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_provider_subscriptions_updated_at 
    BEFORE UPDATE ON provider_subscriptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at 
    BEFORE UPDATE ON payments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at 
    BEFORE UPDATE ON tickets 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ticket_types_updated_at 
    BEFORE UPDATE ON ticket_types 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to generate unique ticket codes
CREATE OR REPLACE FUNCTION generate_ticket_code()
RETURNS TEXT AS $$
DECLARE
    code TEXT;
    exists_count INTEGER;
BEGIN
    LOOP
        code := upper(substring(md5(random()::text) from 1 for 8));
        SELECT COUNT(*) INTO exists_count FROM tickets WHERE code = code;
        IF exists_count = 0 THEN
            EXIT;
        END IF;
    END LOOP;
    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate unique usernames
CREATE OR REPLACE FUNCTION generate_username()
RETURNS TEXT AS $$
DECLARE
    username TEXT;
    exists_count INTEGER;
BEGIN
    LOOP
        username := 'user' || lpad(floor(random() * 999999)::text, 6, '0');
        SELECT COUNT(*) INTO exists_count FROM tickets WHERE username = username;
        IF exists_count = 0 THEN
            EXIT;
        END IF;
    END LOOP;
    RETURN username;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate random passwords
CREATE OR REPLACE FUNCTION generate_password()
RETURNS TEXT AS $$
BEGIN
    RETURN substring(md5(random()::text) from 1 for 8);
END;
$$ LANGUAGE plpgsql;

-- Add default values for ticket generation
ALTER TABLE tickets 
ALTER COLUMN code SET DEFAULT generate_ticket_code(),
ALTER COLUMN username SET DEFAULT generate_username(),
ALTER COLUMN password SET DEFAULT generate_password();

-- Create view for provider analytics
CREATE OR REPLACE VIEW provider_analytics AS
SELECT 
    p.id as provider_id,
    p.business_name,
    p.contact_email,
    p.subscription_status,
    ps.status as subscription_status_detail,
    ps.expiry_date as subscription_expiry,
    COUNT(t.id) as total_tickets,
    COUNT(CASE WHEN t.status = 'active' THEN 1 END) as active_tickets,
    COUNT(CASE WHEN t.status = 'used' THEN 1 END) as used_tickets,
    COUNT(CASE WHEN t.status = 'expired' THEN 1 END) as expired_tickets,
    COALESCE(SUM(CASE WHEN pay.type = 'mpesa_customer_payment' AND pay.status = 'success' THEN pay.amount END), 0) as total_revenue,
    COALESCE(SUM(CASE WHEN pay.type = 'pesapal_provider_subscription' AND pay.status = 'success' THEN pay.amount END), 0) as subscription_payments,
    MAX(t.created_at) as last_ticket_created,
    MAX(pay.created_at) as last_payment
FROM accounts_provider p
LEFT JOIN provider_subscriptions ps ON p.id = ps.provider_id
LEFT JOIN tickets t ON p.id = t.provider_id
LEFT JOIN payments pay ON p.id = pay.provider_id
GROUP BY p.id, p.business_name, p.contact_email, p.subscription_status, ps.status, ps.expiry_date;

-- Create view for platform analytics
CREATE OR REPLACE VIEW platform_analytics AS
SELECT 
    COUNT(DISTINCT p.id) as total_providers,
    COUNT(DISTINCT CASE WHEN p.subscription_status = 'active' THEN p.id END) as active_providers,
    COUNT(DISTINCT ps.id) as total_subscriptions,
    COUNT(DISTINCT CASE WHEN ps.status = 'active' THEN ps.id END) as active_subscriptions,
    COUNT(DISTINCT t.id) as total_tickets,
    COUNT(DISTINCT CASE WHEN t.status = 'active' THEN t.id END) as active_tickets,
    COALESCE(SUM(CASE WHEN pay.type = 'pesapal_provider_subscription' AND pay.status = 'success' THEN pay.amount END), 0) as platform_revenue,
    COALESCE(SUM(CASE WHEN pay.type = 'mpesa_customer_payment' AND pay.status = 'success' THEN pay.amount END), 0) as provider_revenue,
    COUNT(DISTINCT CASE WHEN pay.type = 'mpesa_customer_payment' AND pay.status = 'success' THEN pay.id END) as successful_customer_payments,
    COUNT(DISTINCT CASE WHEN pay.type = 'pesapal_provider_subscription' AND pay.status = 'success' THEN pay.id END) as successful_subscription_payments
FROM accounts_provider p
LEFT JOIN provider_subscriptions ps ON p.id = ps.provider_id
LEFT JOIN tickets t ON p.id = t.provider_id
LEFT JOIN payments pay ON p.id = pay.provider_id;

-- Insert sample subscription plans
INSERT INTO ticket_types (provider_id, name, type, duration_hours, price, is_active, is_featured, description) VALUES
(1, '1 Hour WiFi', 'time', 1, 50.00, true, true, '1 hour of high-speed internet access'),
(1, '24 Hours WiFi', 'time', 24, 200.00, true, true, '24 hours of high-speed internet access'),
(1, '1 Week WiFi', 'time', 168, 1000.00, true, false, '1 week of high-speed internet access'),
(1, '500MB Data', 'data', NULL, 100.00, true, false, '500MB of data usage'),
(1, '1GB Data', 'data', NULL, 150.00, true, true, '1GB of data usage')
ON CONFLICT DO NOTHING;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON provider_subscriptions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON payments TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON tickets TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ticket_types TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ticket_usage TO authenticated;

GRANT SELECT ON provider_analytics TO authenticated;
GRANT SELECT ON platform_analytics TO authenticated;

-- Create indexes for webhook lookups
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(external_txn_id) WHERE external_txn_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_provider_subscriptions_order_id ON provider_subscriptions(order_id) WHERE order_id IS NOT NULL;

-- Add comments for documentation
COMMENT ON TABLE provider_subscriptions IS 'Provider subscription payments via Pesapal';
COMMENT ON TABLE payments IS 'Unified payments table for both Pesapal and M-PESA transactions';
COMMENT ON TABLE tickets IS 'WiFi vouchers/tickets for customer access';
COMMENT ON TABLE ticket_types IS 'WiFi plan definitions per provider';
COMMENT ON TABLE ticket_usage IS 'Usage tracking for WiFi tickets';

COMMENT ON COLUMN payments.type IS 'Payment type: pesapal_provider_subscription or mpesa_customer_payment';
COMMENT ON COLUMN payments.provider_payload IS 'Raw webhook data for auditing and debugging';
COMMENT ON COLUMN tickets.plan_type IS 'Ticket type: time-based or data-based';
COMMENT ON COLUMN tickets.data_used_mb IS 'Data consumed in MB (for data-based tickets)';

-- Migration completed successfully
SELECT 'Database migration completed successfully!' as status;

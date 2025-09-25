-- Sample data for MikroTik Hotspot Config Generator
-- This file contains sample data to populate the database

-- Insert subscription plans
INSERT INTO subscriptions_subscriptionplan (name, description, price, duration_days, features) VALUES
('Basic', 'Perfect for small hotspot providers', 2500.00, 30, '["Unlimited config generation", "All MikroTik models", "Email support", "Config history"]'),
('Professional', 'Ideal for growing ISPs', 5000.00, 30, '["Everything in Basic", "Priority support", "Custom templates", "API access"]'),
('Enterprise', 'For large ISPs and enterprises', 10000.00, 30, '["Everything in Professional", "24/7 phone support", "White-label solution", "Custom integrations"]');

-- Insert MikroTik models
INSERT INTO config_generator_mikrotikmodel (name, model_code, description, is_active) VALUES
('RB750', 'RB750', '5-port router with 1 WAN and 4 LAN ports', TRUE),
('RB951', 'RB951', '5-port router with wireless', TRUE),
('RB2011', 'RB2011', '10-port router with 1 SFP port', TRUE),
('RB3011', 'RB3011', '10-port router with 1 SFP+ port', TRUE),
('RB4011', 'RB4011', '10-port router with 1 SFP+ port and wireless', TRUE),
('RB5009', 'RB5009', '9-port router with 1 SFP+ port', TRUE),
('RB750Gr3', 'RB750Gr3', '5-port router with 1 WAN and 4 LAN ports', TRUE),
('hEX S', 'hEX S', '5-port router with 1 SFP port', TRUE);

-- Insert voucher types
INSERT INTO config_generator_vouchertype (name, duration_hours, description, is_active) VALUES
('1 Hour', 1, 'One hour voucher', TRUE),
('2 Hours', 2, 'Two hour voucher', TRUE),
('4 Hours', 4, 'Four hour voucher', TRUE),
('8 Hours', 8, 'Eight hour voucher', TRUE),
('12 Hours', 12, 'Twelve hour voucher', TRUE),
('24 Hours', 24, 'One day voucher', TRUE),
('3 Days', 72, 'Three day voucher', TRUE),
('1 Week', 168, 'One week voucher', TRUE),
('2 Weeks', 336, 'Two week voucher', TRUE),
('1 Month', 720, 'One month voucher', TRUE);

-- Insert bandwidth profiles
INSERT INTO config_generator_bandwidthprofile (name, download_speed, upload_speed, description, is_active) VALUES
('Basic', '1M', '512K', 'Basic internet speed for light browsing', TRUE),
('Standard', '2M', '1M', 'Standard speed for general use', TRUE),
('Premium', '5M', '2M', 'Premium speed for streaming and downloads', TRUE),
('Business', '10M', '5M', 'Business speed for professional use', TRUE),
('Unlimited', '20M', '10M', 'Unlimited speed for heavy usage', TRUE),
('Gaming', '15M', '8M', 'Optimized for gaming and streaming', TRUE);

-- Insert sample config templates
INSERT INTO config_generator_configtemplate (name, description, mikrotik_model_id, template_content, is_active) VALUES
('Basic Hotspot Setup', 'Basic hotspot configuration with user management', 1, '
# Basic Hotspot Configuration
# Generated for {{ hotspot_name }}

# Set hotspot interface
/interface bridge
add name=hotspot-bridge

# Configure IP address
/ip address
add address={{ hotspot_ip }}/24 interface=hotspot-bridge

# Configure DHCP server
/ip dhcp-server
add address-pool=hotspot-pool interface=hotspot-bridge name=hotspot-dhcp

/ip dhcp-server network
add address={{ hotspot_ip }}/24 gateway={{ hotspot_ip }}

/ip pool
add name=hotspot-pool ranges={{ hotspot_ip | replace("192.168.1.1", "192.168.1.2") }}-{{ hotspot_ip | replace("192.168.1.1", "192.168.1.100") }}

# Configure hotspot
/ip hotspot setup
set hotspot-address={{ hotspot_ip }} dns-name={{ hotspot_name }} certificate=none

# Configure DNS
/ip dns
set servers={{ dns_servers | join(",") }}

# Configure user profile
/ip hotspot user profile
add name=default-profile rate-limit={{ bandwidth_profile.download_speed }}/{{ bandwidth_profile.upload_speed }}

# Configure hotspot server
/ip hotspot
set address={{ hotspot_ip }} name={{ hotspot_name }} profile=default-profile

# Configure firewall rules
/ip firewall filter
add chain=forward action=accept place-before=0 src-address=192.168.1.0/24 dst-address=192.168.1.0/24
add chain=forward action=accept place-before=1 src-address=192.168.1.0/24

# Configure NAT
/ip firewall nat
add action=masquerade chain=srcnat out-interface=ether1

# Create sample vouchers
/ip hotspot user
add name=voucher1 password=12345678 profile=default-profile
add name=voucher2 password=87654321 profile=default-profile
add name=voucher3 password=11111111 profile=default-profile
', TRUE),
('Advanced Hotspot Setup', 'Advanced hotspot configuration with bandwidth management', 2, '
# Advanced Hotspot Configuration
# Generated for {{ hotspot_name }}

# Set hotspot interface
/interface bridge
add name=hotspot-bridge

# Configure IP address
/ip address
add address={{ hotspot_ip }}/24 interface=hotspot-bridge

# Configure DHCP server
/ip dhcp-server
add address-pool=hotspot-pool interface=hotspot-bridge name=hotspot-dhcp

/ip dhcp-server network
add address={{ hotspot_ip }}/24 gateway={{ hotspot_ip }}

/ip pool
add name=hotspot-pool ranges={{ hotspot_ip | replace("192.168.1.1", "192.168.1.2") }}-{{ hotspot_ip | replace("192.168.1.1", "192.168.1.100") }}

# Configure hotspot
/ip hotspot setup
set hotspot-address={{ hotspot_ip }} dns-name={{ hotspot_name }} certificate=none

# Configure DNS
/ip dns
set servers={{ dns_servers | join(",") }}

# Configure user profiles
/ip hotspot user profile
add name=basic-profile rate-limit=1M/512K
add name=standard-profile rate-limit=2M/1M
add name=premium-profile rate-limit=5M/2M

# Configure hotspot server
/ip hotspot
set address={{ hotspot_ip }} name={{ hotspot_name }} profile=basic-profile

# Configure firewall rules
/ip firewall filter
add chain=forward action=accept place-before=0 src-address=192.168.1.0/24 dst-address=192.168.1.0/24
add chain=forward action=accept place-before=1 src-address=192.168.1.0/24

# Configure NAT
/ip firewall nat
add action=masquerade chain=srcnat out-interface=ether1

# Configure bandwidth management
/queue simple
add name=hotspot-queue target=192.168.1.0/24 max-limit={{ bandwidth_profile.download_speed }}/{{ bandwidth_profile.upload_speed }}

# Create sample vouchers
/ip hotspot user
add name=voucher1 password=12345678 profile=basic-profile
add name=voucher2 password=87654321 profile=standard-profile
add name=voucher3 password=11111111 profile=premium-profile
', TRUE);

-- Create a sample admin user (password: admin123)
INSERT INTO accounts_user (username, email, password, is_staff, is_superuser, is_active, first_name, last_name, phone_number, company_name, is_verified) VALUES
('admin', 'admin@hotspotconfig.com', 'pbkdf2_sha256$260000$admin123$admin123', TRUE, TRUE, TRUE, 'Admin', 'User', '+254700000000', 'Hotspot Config', TRUE);

-- Create a sample regular user (password: user123)
INSERT INTO accounts_user (username, email, password, is_staff, is_superuser, is_active, first_name, last_name, phone_number, company_name, is_verified) VALUES
('testuser', 'test@example.com', 'pbkdf2_sha256$260000$user123$user123', FALSE, FALSE, TRUE, 'Test', 'User', '+254700000001', 'Test Company', TRUE);

-- Create sample subscription for test user
INSERT INTO subscriptions_subscription (user_id, plan_id, status, start_date, end_date, is_active, auto_renew) VALUES
(2, 1, 'active', NOW(), NOW() + INTERVAL '30 days', TRUE, FALSE);

-- Create sample subscription usage
INSERT INTO subscriptions_subscriptionusage (subscription_id, configs_generated, last_used) VALUES
(1, 5, NOW());

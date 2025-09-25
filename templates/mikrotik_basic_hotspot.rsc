# MikroTik Basic Hotspot Configuration
# Generated for {{ hotspot_name }}
# Created: {{ created_at }}
# User: {{ user.email }}

# ===========================================
# BASIC HOTSPOT SETUP
# ===========================================

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

# ===========================================
# FIREWALL RULES
# ===========================================

# Configure firewall rules
/ip firewall filter
add chain=forward action=accept place-before=0 src-address=192.168.1.0/24 dst-address=192.168.1.0/24
add chain=forward action=accept place-before=1 src-address=192.168.1.0/24

# Configure NAT
/ip firewall nat
add action=masquerade chain=srcnat out-interface=ether1

# ===========================================
# BANDWIDTH MANAGEMENT
# ===========================================

# Configure bandwidth management
/queue simple
add name=hotspot-queue target=192.168.1.0/24 max-limit={{ bandwidth_profile.download_speed }}/{{ bandwidth_profile.upload_speed }}

# ===========================================
# SAMPLE VOUCHERS
# ===========================================

# Create sample vouchers
/ip hotspot user
add name=voucher1 password=12345678 profile=default-profile
add name=voucher2 password=87654321 profile=default-profile
add name=voucher3 password=11111111 profile=default-profile
add name=voucher4 password=22222222 profile=default-profile
add name=voucher5 password=33333333 profile=default-profile

# ===========================================
# ADDITIONAL CONFIGURATION
# ===========================================

# Configure hotspot walled garden (optional)
/ip hotspot walled-garden ip
add dst-address=192.168.1.1

# Configure hotspot user manager
/ip hotspot user manager
set allowed-address=192.168.1.0/24

# Configure hotspot active users
/ip hotspot active
# This will show active users when executed

# ===========================================
# SECURITY SETTINGS
# ===========================================

# Configure firewall to block unwanted traffic
/ip firewall filter
add chain=input action=drop connection-state=invalid
add chain=input action=accept connection-state=established,related
add chain=input action=accept in-interface=hotspot-bridge
add chain=input action=drop

# Configure hotspot to use HTTPS (optional)
/ip hotspot profile
set default use-https=yes

# ===========================================
# MONITORING AND LOGGING
# ===========================================

# Enable hotspot logging
/system logging
add topics=hotspot action=memory

# Configure SNMP (optional)
/snmp
set enabled=yes contact="Hotspot Administrator" location="{{ hotspot_name }}"

# ===========================================
# BACKUP CONFIGURATION
# ===========================================

# Create backup
/system backup save name=hotspot-backup

# ===========================================
# END OF CONFIGURATION
# ===========================================

# Configuration completed successfully!
# Total users configured: {{ max_users }}
# Voucher duration: {{ voucher_type.duration_hours }} hours
# Bandwidth limit: {{ bandwidth_profile.download_speed }}/{{ bandwidth_profile.upload_speed }}
# DNS servers: {{ dns_servers | join(",") }}

# MikroTik Hotspot Configuration with Billing Template Support
# Generated for: {{ user.email }}
# Template: {{ template.name }}
{% if billing_template %}
# Billing Template: {{ billing_template.name }}
# Bandwidth: {{ bandwidth_mbps }}Mbps down / {{ upload_mbps }}Mbps up
# Duration: {{ duration_value }} {{ duration_type }}(s)
{% endif %}
# Generated on: {{ "now"|strftime("%Y-%m-%d %H:%M:%S") }}

# System Identity
/system identity set name="{{ hotspot_name }}"

# IP Configuration
/ip address add address={{ hotspot_ip }}/24 interface=ether1

# DNS Configuration
/ip dns set servers={{ dns_servers|join(',') }}

# Hotspot Server Configuration
/ip hotspot setup profile name=hsprof1
/ip hotspot profile set hsprof1 dns-name="{{ hotspot_name }}.local" html-directory=hotspot

# Hotspot Server
/ip hotspot add interface=ether1 name=hotspot1 profile=hsprof1

# User Profile for Billing Template
{% if billing_template %}
/ip hotspot user profile add name="{{ billing_template.name }}" 
    {% if upload_mbps != bandwidth_mbps %}
    rate-limit="{{ bandwidth_mbps }}M/{{ upload_mbps }}M"
    {% else %}
    rate-limit="{{ bandwidth_mbps }}M"
    {% endif %}
    session-timeout={{ duration_seconds }}
    keepalive-timeout=2m
    status-html="/hotspot-status.html"
{% endif %}

# Default User Profile
/ip hotspot user profile add name="default" 
    rate-limit="1M/1M" 
    session-timeout=1h
    keepalive-timeout=2m
    status-html="/hotspot-status.html"

# Voucher Configuration
/ip hotspot user add name="admin" password="admin123" profile="default"

# Queue Configuration for Bandwidth Management
{% if billing_template %}
/queue simple add name="{{ billing_template.name }}_queue" 
    target=ether1 
    {% if upload_mbps != bandwidth_mbps %}
    max-limit="{{ bandwidth_mbps }}M/{{ upload_mbps }}M"
    {% else %}
    max-limit="{{ bandwidth_mbps }}M"
    {% endif %}
    comment="Queue for {{ billing_template.name }}"
{% endif %}

# Default Queue
/queue simple add name="default_queue" 
    target=ether1 
    max-limit="1M/1M" 
    comment="Default queue"

# Firewall Rules
/ip firewall filter add chain=forward action=accept connection-state=established,related
/ip firewall filter add chain=forward action=drop connection-state=invalid
/ip firewall filter add chain=forward action=drop connection-state=new connection-nat-state=!dstnat

# NAT Configuration
/ip firewall nat add chain=srcnat action=masquerade out-interface=ether1

# Hotspot User Management
/ip hotspot user add name="test_user" password="test123" 
    {% if billing_template %}
    profile="{{ billing_template.name }}"
    {% else %}
    profile="default"
    {% endif %}

# Voucher Generation Script
:local voucherLength {{ voucher_length }};
:local voucherPrefix "{{ voucher_prefix }}";
:local maxUsers {{ max_users }};

# Generate sample vouchers
:for i from=1 to=5 do={
    :local voucherCode ($voucherPrefix . [:pick "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" ([:len "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"] * [:rndnum 0 1]) [:rndnum 1 $voucherLength]]);
    /ip hotspot user add name=$voucherCode password=$voucherCode 
        {% if billing_template %}
        profile="{{ billing_template.name }}"
        {% else %}
        profile="default"
        {% endif %}
        comment="Auto-generated voucher"
}

# Logging
/log print info message="Hotspot configuration applied successfully"
/log print info message="Billing template: {{ billing_template.name if billing_template else 'None' }}"
/log print info message="Bandwidth: {{ bandwidth_mbps if billing_template else 'Default' }}Mbps"
/log print info message="Duration: {{ duration_value if billing_template else 'Default' }} {{ duration_type if billing_template else 'hours' }}"

# Configuration Complete
:put "MikroTik Hotspot Configuration Complete"
:put "Hotspot Name: {{ hotspot_name }}"
:put "Hotspot IP: {{ hotspot_ip }}"
{% if billing_template %}
:put "Billing Template: {{ billing_template.name }}"
:put "Bandwidth: {{ bandwidth_mbps }}Mbps down / {{ upload_mbps }}Mbps up"
:put "Duration: {{ duration_value }} {{ duration_type }}(s)"
{% endif %}
:put "DNS Servers: {{ dns_servers|join(', ') }}"
:put "Max Users: {{ max_users }}"
:put "Voucher Length: {{ voucher_length }}"

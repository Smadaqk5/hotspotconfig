from django.template import Template, Context
from django.utils import timezone
from datetime import datetime, timedelta
import secrets
import string

class MikroTikConfigGenerator:
    """Generate MikroTik RouterOS configuration files"""
    
    def __init__(self, provider):
        self.provider = provider
        self.config_sections = []
    
    def generate_basic_config(self):
        """Generate basic MikroTik hotspot configuration"""
        
        # System identity
        self.add_section("System Identity", f"""
# Set router identity
/system identity set name="{self.provider.business_name} Hotspot"
""")
        
        # IP configuration
        self.add_section("IP Configuration", f"""
# Configure IP addresses
/ip address add address=192.168.1.1/24 interface=ether2 comment="Hotspot Network"
/ip address add address=10.0.0.1/24 interface=ether3 comment="Management Network"
""")
        
        # DHCP Server
        self.add_section("DHCP Server", f"""
# Configure DHCP server for hotspot
/ip dhcp-server add interface=ether2 address-pool=hotspot-pool disabled=no
/ip pool add name=hotspot-pool ranges=192.168.1.10-192.168.1.254
/ip dhcp-server network add address=192.168.1.0/24 gateway=192.168.1.1 dns-server=8.8.8.8,8.8.4.4
""")
        
        # Hotspot Server
        self.add_section("Hotspot Server", f"""
# Configure hotspot server
/ip hotspot setup
/ip hotspot profile add name=hsprof1 dns-name="{self.provider.business_name.lower().replace(' ', '-')}.local" html-directory=hotspot login-by=http,https,ftp
/ip hotspot add name=hs1 interface=ether2 profile=hsprof1 address-pool=hotspot-pool
""")
        
        # User management
        self.add_section("User Management", f"""
# Hotspot users will be managed via API
# Users are created dynamically when tickets are purchased
""")
        
        # Firewall rules
        self.add_section("Firewall Rules", f"""
# Basic firewall configuration
/ip firewall filter add chain=input action=accept connection-state=established,related
/ip firewall filter add chain=input action=accept src-address=192.168.1.0/24
/ip firewall filter add chain=input action=accept src-address=10.0.0.0/24
/ip firewall filter add chain=input action=drop

# Allow hotspot traffic
/ip firewall filter add chain=forward action=accept src-address=192.168.1.0/24 dst-address=192.168.1.0/24
/ip firewall filter add chain=forward action=accept src-address=192.168.1.0/24 dst-address=!192.168.1.0/24
""")
        
        # NAT rules
        self.add_section("NAT Rules", f"""
# NAT configuration for internet access
/ip firewall nat add chain=srcnat action=masquerade out-interface=ether1
""")
        
        # Bandwidth limits
        self.add_section("Bandwidth Limits", f"""
# Bandwidth limiting for different ticket types
# These will be applied based on user profiles
""")
        
        return self.get_full_config()
    
    def generate_advanced_config(self, ticket_types):
        """Generate advanced configuration with ticket type support"""
        
        # Start with basic config
        self.generate_basic_config()
        
        # Add ticket type specific configurations
        self.add_section("Ticket Type Profiles", self.generate_ticket_profiles(ticket_types))
        
        # Add API integration
        self.add_section("API Integration", self.generate_api_config())
        
        # Add monitoring
        self.add_section("Monitoring", self.generate_monitoring_config())
        
        return self.get_full_config()
    
    def generate_ticket_profiles(self, ticket_types):
        """Generate user profiles for different ticket types"""
        config = []
        
        for ticket_type in ticket_types:
            profile_name = f"profile_{ticket_type.id}"
            
            # Create user profile
            config.append(f"""
# Profile for {ticket_type.name}
/ip hotspot user profile add name={profile_name}""")
            
            # Set bandwidth limits
            if ticket_type.download_speed_mbps:
                config.append(f"/ip hotspot user profile set {profile_name} rate-limit={ticket_type.download_speed_mbps}M/{ticket_type.upload_speed_mbps}M")
            
            # Set session timeout for time-based tickets
            if ticket_type.type == 'time':
                config.append(f"/ip hotspot user profile set {profile_name} session-timeout={ticket_type.duration_hours * 3600}")
            
            # Set data limit for data-based tickets
            if ticket_type.type == 'data':
                config.append(f"/ip hotspot user profile set {profile_name} bytes-in-limit={ticket_type.data_limit_mb * 1024 * 1024}")
        
        return "\n".join(config)
    
    def generate_api_config(self):
        """Generate API configuration for dynamic user management"""
        return f"""
# API configuration for dynamic user management
/ip service set api disabled=no
/ip service set api port=8728
/ip service set api address=10.0.0.0/24

# Script for user management
/system script add name=add-user source={{
    /ip hotspot user add name=$username password=$password profile=$profile
}}

/system script add name=remove-user source={{
    /ip hotspot user remove [find name=$username]
}}

/system script add name=update-user source={{
    /ip hotspot user set [find name=$username] password=$password profile=$profile
}}
"""
    
    def generate_monitoring_config(self):
        """Generate monitoring and logging configuration"""
        return f"""
# Monitoring and logging
/log print info message="Hotspot user connected: $user"
/log print info message="Hotspot user disconnected: $user"

# SNMP configuration for monitoring
/snmp set enabled=yes contact="{self.provider.contact_email}" location="{self.provider.address}"
/snmp community set public addresses=10.0.0.0/24
"""
    
    def generate_captive_portal_config(self):
        """Generate captive portal configuration"""
        return f"""
# Captive portal customization
/ip hotspot profile set hsprof1 html-directory=hotspot
/ip hotspot profile set hsprof1 http-proxy=0.0.0.0:0
/ip hotspot profile set hsprof1 use-radius=no

# Custom login page
/file add name=login.html contents="<!DOCTYPE html>
<html>
<head>
    <title>{self.provider.business_name} WiFi</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
        .container {{ max-width: 400px; margin: 0 auto; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px; }}
        .form {{ background: #f5f5f5; padding: 20px; border-radius: 10px; }}
        input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
        button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class='container'>
        <div class='logo'>{self.provider.business_name}</div>
        <div class='form'>
            <h3>WiFi Access</h3>
            <form method='post' action='$linklogin'>
                <input type='hidden' name='dst' value='$linkorig'>
                <input type='hidden' name='popup' value='true'>
                <input type='text' name='username' placeholder='Username' required>
                <input type='password' name='password' placeholder='Password' required>
                <button type='submit'>Connect</button>
            </form>
        </div>
    </div>
</body>
</html>"
"""
    
    def add_section(self, title, content):
        """Add a configuration section"""
        section = f"""
# {title}
{content}
"""
        self.config_sections.append(section)
    
    def get_full_config(self):
        """Get the complete configuration"""
        config = f"""# MikroTik RouterOS Configuration
# Generated for {self.provider.business_name}
# Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
# Provider ID: {self.provider.id}

"""
        
        for section in self.config_sections:
            config += section + "\n"
        
        return config
    
    def generate_user_script(self, ticket):
        """Generate script to add a specific user"""
        return f"""
# Add user for ticket {ticket.code}
/ip hotspot user add name={ticket.username} password={ticket.password} profile=profile_{ticket.ticket_type.id}
"""
    
    def generate_remove_user_script(self, ticket):
        """Generate script to remove a specific user"""
        return f"""
# Remove user for ticket {ticket.code}
/ip hotspot user remove [find name={ticket.username}]
"""
    
    @staticmethod
    def generate_radius_config(provider):
        """Generate RADIUS configuration for advanced setups"""
        return f"""
# RADIUS configuration for {provider.business_name}
/radius add service=hotspot address={provider.radius_server} secret={provider.radius_secret} timeout=5s
/ip hotspot set hs1 use-radius=yes
"""
    
    @staticmethod
    def generate_backup_script():
        """Generate backup script"""
        return f"""
# Backup script
/system backup save name=hotspot-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}
"""

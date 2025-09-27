"""
MikroTik RouterOS Configuration Generator
"""
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import MikroTikModel, VoucherType, BandwidthProfile, ConfigTemplate, GeneratedConfig
from accounts.models import Provider
import uuid
import secrets
import string


class MikroTikConfigGenerator:
    """Generate MikroTik RouterOS configuration files"""
    
    def __init__(self, provider):
        self.provider = provider
    
    def generate_basic_hotspot_config(self, router_ip="192.168.1.1", hotspot_ip="192.168.1.0/24"):
        """Generate basic hotspot configuration"""
        config = f"""
# MikroTik Hotspot Configuration for {self.provider.business_name}
# Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

# Set router identity
/system identity set name="{self.provider.business_name} Hotspot"

# Configure IP pool for hotspot users
/ip pool add name=hotspot-pool ranges={hotspot_ip}

# Configure hotspot server
/ip hotspot setup set enabled=yes interface=ether2 ip-address={router_ip} ip-pool=hotspot-pool

# Configure hotspot profile
/ip hotspot profile set [find name="hsprof1"] name=default dns-name="{self.provider.business_name}" html-directory-override=hotspot1

# Configure user manager
/user manager set enabled=yes

# Configure user manager database
/user manager database set type=local

# Configure hotspot user profile
/ip hotspot user profile add name=default local-address={router_ip} remote-address=hotspot-pool

# Configure bandwidth profiles for different ticket types
"""
        
        # Add bandwidth profiles for each ticket type
        for ticket_type in self.provider.ticket_types.all():
            if ticket_type.ticket_type == 'time':
                # Time-based tickets
                config += f"""
# Profile for {ticket_type.name} ({ticket_type.value} hours)
/ip hotspot user profile add name="{ticket_type.name}" local-address={router_ip} remote-address=hotspot-pool
"""
            else:
                # Data-based tickets
                config += f"""
# Profile for {ticket_type.name} ({ticket_type.value} GB)
/ip hotspot user profile add name="{ticket_type.name}" local-address={router_ip} remote-address=hotspot-pool
"""
        
        # Add firewall rules
        config += """
# Firewall rules for hotspot
/ip firewall filter add chain=forward action=accept src-address=192.168.1.0/24 dst-address=192.168.1.0/24
/ip firewall filter add chain=forward action=accept src-address=192.168.1.0/24 dst-address=!192.168.1.0/24

# NAT rules
/ip firewall nat add chain=srcnat action=masquerade src-address=192.168.1.0/24
"""
        
        return config
    
    def generate_advanced_hotspot_config(self, router_ip="192.168.1.1", hotspot_ip="192.168.1.0/24"):
        """Generate advanced hotspot configuration with custom branding"""
        config = f"""
# Advanced MikroTik Hotspot Configuration for {self.provider.business_name}
# Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

# Set router identity
/system identity set name="{self.provider.business_name} Hotspot"

# Configure logging
/system logging add topics=hotspot,info action=memory

# Configure IP pool for hotspot users
/ip pool add name=hotspot-pool ranges={hotspot_ip}

# Configure hotspot server with custom settings
/ip hotspot setup set enabled=yes interface=ether2 ip-address={router_ip} ip-pool=hotspot-pool

# Configure hotspot profile with custom branding
/ip hotspot profile set [find name="hsprof1"] name=default dns-name="{self.provider.business_name}" html-directory-override=hotspot1

# Configure user manager
/user manager set enabled=yes

# Configure user manager database
/user manager database set type=local

# Configure hotspot user profile
/ip hotspot user profile add name=default local-address={router_ip} remote-address=hotspot-pool

# Configure bandwidth profiles for different ticket types
"""
        
        # Add bandwidth profiles for each ticket type
        for ticket_type in self.provider.ticket_types.all():
            if ticket_type.ticket_type == 'time':
                # Time-based tickets with time limits
                config += f"""
# Profile for {ticket_type.name} ({ticket_type.value} hours)
/ip hotspot user profile add name="{ticket_type.name}" local-address={router_ip} remote-address=hotspot-pool
"""
            else:
                # Data-based tickets with data limits
                config += f"""
# Profile for {ticket_type.name} ({ticket_type.value} GB)
/ip hotspot user profile add name="{ticket_type.name}" local-address={router_ip} remote-address=hotspot-pool
"""
        
        # Add firewall rules
        config += """
# Firewall rules for hotspot
/ip firewall filter add chain=forward action=accept src-address=192.168.1.0/24 dst-address=192.168.1.0/24
/ip firewall filter add chain=forward action=accept src-address=192.168.1.0/24 dst-address=!192.168.1.0/24

# NAT rules
/ip firewall nat add chain=srcnat action=masquerade src-address=192.168.1.0/24

# Rate limiting for different user types
/ip hotspot user profile set default rate-limit="1M/1M"
"""
        
        return config
    
    def generate_user_script(self, ticket_code, username, password, ticket_type, expiry_hours=None):
        """Generate user creation script for a specific ticket"""
        script = f"""
# Add user for ticket: {ticket_code}
# Username: {username}
# Password: {password}
# Ticket Type: {ticket_type.name}
"""
        
        if ticket_type.ticket_type == 'time' and expiry_hours:
            script += f"""
# Time-based ticket: {expiry_hours} hours
/ip hotspot user add name="{username}" password="{password}" profile="{ticket_type.name}" limit-uptime="{expiry_hours}h"
"""
        else:
            script += f"""
# Data-based ticket: {ticket_type.value} GB
/ip hotspot user add name="{username}" password="{password}" profile="{ticket_type.name}"
"""
        
        return script
    
    def generate_batch_users_script(self, tickets):
        """Generate script to add multiple users at once"""
        script = f"""
# Batch user creation for {len(tickets)} tickets
# Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        for ticket in tickets:
            script += self.generate_user_script(
                ticket.code,
                ticket.username,
                ticket.password,
                ticket.ticket_type,
                ticket_type.value if ticket.ticket_type.ticket_type == 'time' else None
            )
        
        return script
    
    def generate_cleanup_script(self, expired_tickets):
        """Generate script to remove expired users"""
        script = f"""
# Cleanup expired users
# Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        for ticket in expired_tickets:
            script += f"""
# Remove expired user: {ticket.username}
/ip hotspot user remove [find name="{ticket.username}"]
"""
        
        return script
    
    def save_config_to_file(self, config_content, filename=None):
        """Save configuration to a file"""
        if not filename:
            filename = f"{self.provider.business_name}_hotspot_config_{timezone.now().strftime('%Y%m%d_%H%M%S')}.rsc"
        
        # Create GeneratedConfig record
        generated_config = GeneratedConfig.objects.create(
            provider=self.provider,
            config_type='hotspot',
            filename=filename,
            content=config_content,
            is_active=True
        )
        
        return generated_config
    
    def download_config(self, config_id):
        """Download configuration file"""
        try:
            config = GeneratedConfig.objects.get(id=config_id, provider=self.provider)
            
            response = HttpResponse(config.content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{config.filename}"'
            return response
        except GeneratedConfig.DoesNotExist:
            return None

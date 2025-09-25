"""
Security utilities and middleware for the hotspot config application
"""
import hashlib
import hmac
import json
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re


class PesapalSignatureValidator:
    """Validate Pesapal webhook signatures"""
    
    @staticmethod
    def verify_signature(payload, signature, secret):
        """Verify Pesapal webhook signature"""
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware"""
    
    def process_request(self, request):
        # Simple rate limiting based on IP
        client_ip = self.get_client_ip(request)
        
        # Check if IP is in rate limit cache
        # This is a simplified implementation
        # In production, use Redis or similar for rate limiting
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses"""
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


def validate_hotspot_ip(ip_address):
    """Validate hotspot IP address"""
    import ipaddress
    
    try:
        ip = ipaddress.ip_address(ip_address)
        # Check if it's a private IP address
        if not ip.is_private:
            raise ValidationError("Hotspot IP must be a private IP address")
        return True
    except ValueError:
        raise ValidationError("Invalid IP address format")


def validate_dns_servers(dns_servers):
    """Validate DNS servers"""
    import ipaddress
    
    servers = dns_servers.split(',')
    for server in servers:
        server = server.strip()
        try:
            ipaddress.ip_address(server)
        except ValueError:
            raise ValidationError(f"Invalid DNS server: {server}")


def validate_config_name(name):
    """Validate configuration name"""
    if not name or len(name.strip()) < 3:
        raise ValidationError("Configuration name must be at least 3 characters")
    
    if len(name) > 200:
        raise ValidationError("Configuration name must be less than 200 characters")
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValidationError("Configuration name contains invalid characters")


def validate_hotspot_name(name):
    """Validate hotspot name"""
    if not name or len(name.strip()) < 3:
        raise ValidationError("Hotspot name must be at least 3 characters")
    
    if len(name) > 100:
        raise ValidationError("Hotspot name must be less than 100 characters")
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValidationError("Hotspot name contains invalid characters")


def sanitize_template_input(user_input):
    """Sanitize user input for template rendering"""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
    
    for char in dangerous_chars:
        user_input = user_input.replace(char, '')
    
    return user_input.strip()


def validate_payment_amount(amount):
    """Validate payment amount"""
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than 0")
        if amount > 100000:  # Maximum 100,000 KES
            raise ValidationError("Payment amount too large")
        return amount
    except (ValueError, TypeError):
        raise ValidationError("Invalid payment amount")


def validate_phone_number(phone):
    """Validate Kenyan phone number"""
    if not phone:
        return True  # Phone number is optional
    
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Kenyan number
    if phone.startswith('254'):
        if len(phone) == 12:
            return phone
    elif phone.startswith('0'):
        if len(phone) == 10:
            return '254' + phone[1:]
    elif phone.startswith('7'):
        if len(phone) == 9:
            return '254' + phone
    
    raise ValidationError("Invalid Kenyan phone number format")


def validate_email_address(email):
    """Validate email address"""
    try:
        validate_email(email)
        return email.lower()
    except ValidationError:
        raise ValidationError("Invalid email address format")


class InputValidator:
    """Comprehensive input validation"""
    
    @staticmethod
    def validate_config_generation_data(data):
        """Validate config generation input data"""
        errors = {}
        
        # Validate config name
        try:
            validate_config_name(data.get('config_name', ''))
        except ValidationError as e:
            errors['config_name'] = str(e)
        
        # Validate hotspot name
        try:
            validate_hotspot_name(data.get('hotspot_name', ''))
        except ValidationError as e:
            errors['hotspot_name'] = str(e)
        
        # Validate hotspot IP
        try:
            validate_hotspot_ip(data.get('hotspot_ip', ''))
        except ValidationError as e:
            errors['hotspot_ip'] = str(e)
        
        # Validate DNS servers
        try:
            validate_dns_servers(data.get('dns_servers', ''))
        except ValidationError as e:
            errors['dns_servers'] = str(e)
        
        # Validate max users
        try:
            max_users = int(data.get('max_users', 0))
            if max_users < 1 or max_users > 1000:
                errors['max_users'] = "Max users must be between 1 and 1000"
        except (ValueError, TypeError):
            errors['max_users'] = "Invalid max users value"
        
        return errors
    
    @staticmethod
    def validate_payment_data(data):
        """Validate payment input data"""
        errors = {}
        
        # Validate amount
        try:
            validate_payment_amount(data.get('amount', 0))
        except ValidationError as e:
            errors['amount'] = str(e)
        
        # Validate plan ID
        try:
            plan_id = int(data.get('plan_id', 0))
            if plan_id <= 0:
                errors['plan_id'] = "Invalid plan ID"
        except (ValueError, TypeError):
            errors['plan_id'] = "Plan ID must be a valid integer"
        
        return errors
    
    @staticmethod
    def validate_user_registration_data(data):
        """Validate user registration data"""
        errors = {}
        
        # Validate email
        try:
            validate_email_address(data.get('email', ''))
        except ValidationError as e:
            errors['email'] = str(e)
        
        # Validate password
        password = data.get('password', '')
        if len(password) < 8:
            errors['password'] = "Password must be at least 8 characters"
        
        # Validate phone number
        try:
            validate_phone_number(data.get('phone_number', ''))
        except ValidationError as e:
            errors['phone_number'] = str(e)
        
        return errors

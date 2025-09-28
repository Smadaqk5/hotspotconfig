"""
Custom middleware for handling Content Security Policy
"""
from django.conf import settings

class CSPMiddleware:
    """Middleware to add Content Security Policy headers"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Set very permissive CSP headers to avoid conflicts with browser extensions
        # This ensures inline scripts work in all environments including Heroku
        csp_policy = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Override any existing CSP headers
        response['Content-Security-Policy'] = csp_policy
        response['Content-Security-Policy-Report-Only'] = None  # Remove report-only headers
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response

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
        
        # In development or if CSP is disabled, don't set CSP headers
        if getattr(settings, 'DEBUG', False) or getattr(settings, 'DISABLE_CSP', False):
            # Remove any existing CSP headers in development
            response.pop('Content-Security-Policy', None)
            response.pop('Content-Security-Policy-Report-Only', None)
            return response
        
        # Set very permissive CSP headers to avoid conflicts with browser extensions
        # This ensures inline scripts work in all environments including Heroku
        csp_policy = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: chrome-extension:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https: chrome-extension:; "
            "style-src 'self' 'unsafe-inline' https: chrome-extension:; "
            "img-src 'self' data: https: blob: chrome-extension:; "
            "font-src 'self' https: chrome-extension:; "
            "connect-src 'self' https: chrome-extension:; "
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

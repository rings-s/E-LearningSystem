# back/accounts/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import logging

security_logger = logging.getLogger('security')

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.github.com; "
            "frame-ancestors 'none';"
        )
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response

class SecurityLogMiddleware(MiddlewareMixin):
    """
    Log security-related events
    """
    def process_request(self, request):
        # Log suspicious requests
        if self.is_suspicious_request(request):
            security_logger.warning(
                f"Suspicious request from {request.META.get('REMOTE_ADDR')}: "
                f"{request.method} {request.path}"
            )
        return None
    
    def is_suspicious_request(self, request):
        """Check for suspicious request patterns"""
        suspicious_patterns = [
            'admin/login',
            'wp-admin',
            'phpmyadmin',
            '.php',
            'eval(',
            'script>',
        ]
        
        path = request.path.lower()
        return any(pattern in path for pattern in suspicious_patterns)

class WebSocketAuthMiddleware(MiddlewareMixin):
    """
    Custom middleware for WebSocket authentication if needed.
    """
    def process_request(self, request):
        return None
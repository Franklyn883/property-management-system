from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import re


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Custom middleware to add comprehensive security headers.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to the response.
        """
        # Content Security Policy (CSP)
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.example.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests;"
        )
        response['Content-Security-Policy'] = csp_policy
        
        # X-Frame-Options (prevent clickjacking)
        response['X-Frame-Options'] = 'DENY'
        
        # X-Content-Type-Options (prevent MIME type sniffing)
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-XSS-Protection (XSS protection)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature Policy)
        permissions_policy = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "encrypted-media=(), "
            "picture-in-picture=()"
        )
        response['Permissions-Policy'] = permissions_policy
        
        # Strict-Transport-Security (HSTS)
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Cache Control for sensitive endpoints
        if self._is_sensitive_endpoint(request.path):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
    def _is_sensitive_endpoint(self, path):
        """
        Check if the endpoint is sensitive and should not be cached.
        """
        sensitive_patterns = [
            r'^/api/auth/',
            r'^/api/admin/',
            r'^/api/profile/',
            r'^/api/internal/',
        ]
        
        for pattern in sensitive_patterns:
            if re.match(pattern, path):
                return True
        return False


class CORSMiddleware(MiddlewareMixin):
    """
    Custom CORS middleware with enhanced security.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [
            'http://localhost:3000',
            'http://localhost:8000',
            'https://localhost:3000',
            'https://localhost:8000',
        ])
        self.allowed_methods = getattr(settings, 'CORS_ALLOWED_METHODS', [
            'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'
        ])
        self.allowed_headers = getattr(settings, 'CORS_ALLOWED_HEADERS', [
            'Content-Type',
            'Authorization',
            'X-Requested-With',
            'Accept',
            'Origin',
            'X-Internal-Api-Key',
        ])
        self.expose_headers = getattr(settings, 'CORS_EXPOSE_HEADERS', [
            'Content-Type',
            'X-Total-Count',
            'X-Page-Count',
        ])
        self.max_age = getattr(settings, 'CORS_MAX_AGE', 86400)  # 24 hours
    
    def process_request(self, request):
        """
        Handle preflight OPTIONS requests.
        """
        if request.method == 'OPTIONS':
            origin = request.META.get('HTTP_ORIGIN')
            
            if origin in self.allowed_origins:
                response = HttpResponse()
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
                response['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
                response['Access-Control-Max-Age'] = str(self.max_age)
                response['Access-Control-Allow-Credentials'] = 'true'
                return response
        
        return None
    
    def process_response(self, request, response):
        """
        Add CORS headers to the response.
        """
        origin = request.META.get('HTTP_ORIGIN')
        
        if origin in self.allowed_origins:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
            response['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
            response['Access-Control-Expose-Headers'] = ', '.join(self.expose_headers)
            response['Access-Control-Allow-Credentials'] = 'true'
        
        return response


class SecurityAuditMiddleware(MiddlewareMixin):
    """
    Middleware for security audit logging.
    """
    
    def process_request(self, request):
        """
        Log security-relevant request information.
        """
        # Log suspicious requests
        self._log_suspicious_request(request)
        return None
    
    def _log_suspicious_request(self, request):
        """
        Log requests that might be suspicious.
        """
        suspicious_patterns = [
            r'\.\./',  # Directory traversal
            r'<script',  # XSS attempts
            r'javascript:',  # JavaScript injection
            r'union\s+select',  # SQL injection
            r'exec\s*\(',  # Command injection
        ]
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        path = request.path
        method = request.method
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE) or \
               re.search(pattern, path, re.IGNORECASE):
                self._log_security_event(request, f"Suspicious request pattern: {pattern}")
                break
    
    def _log_security_event(self, request, message):
        """
        Log security events.
        """
        import logging
        logger = logging.getLogger('security')
        
        log_data = {
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'path': request.path,
            'method': request.method,
            'message': message,
        }
        
        logger.warning(f"Security event: {log_data}")
    
    def _get_client_ip(self, request):
        """
        Get the client's real IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 
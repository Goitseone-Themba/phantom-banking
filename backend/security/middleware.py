from django.http import HttpResponseForbidden
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import re
import json

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile CSRF exempt URLs
        self.csrf_exempt_urls = [re.compile(url) for url in getattr(settings, 'CSRF_EXEMPT_URLS', [])]

    def __call__(self, request):
        # Check for basic security headers
        if not self._check_security_headers(request):
            return HttpResponseForbidden("Invalid security headers")

        # Rate limiting
        if not self._check_rate_limit(request):
            return HttpResponseForbidden("Rate limit exceeded")

        # Add security headers to response
        response = self.get_response(request)
        self._add_security_headers(response)
        
        return response

    def _check_security_headers(self, request):
        # Verify origin for CORS requests
        if request.META.get('HTTP_ORIGIN'):
            if request.META['HTTP_ORIGIN'] not in settings.ALLOWED_ORIGINS:
                return False

        # Verify content type for POST requests
        if request.method == 'POST':
            content_type = request.META.get('CONTENT_TYPE', '')
            if not content_type.startswith(('application/json', 'multipart/form-data')):
                return False

        return True

    def _check_rate_limit(self, request):
        if not request.user.is_authenticated:
            return True  # Rate limiting for authenticated users only

        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Create cache keys for different rate limit windows
        user_key = f"rate_limit:{request.user.id}"
        ip_key = f"rate_limit:{client_ip}"
        
        # Check minute rate limit (60 requests per minute)
        minute_requests = cache.get(f"{user_key}:minute", 0)
        if minute_requests >= 60:
            return False
        
        # Check hour rate limit (1000 requests per hour)
        hour_requests = cache.get(f"{user_key}:hour", 0)
        if hour_requests >= 1000:
            return False
        
        # Increment counters
        cache.set(f"{user_key}:minute", minute_requests + 1, 60)  # Expires in 60 seconds
        cache.set(f"{user_key}:hour", hour_requests + 1, 3600)    # Expires in 1 hour
        
        return True

    def _add_security_headers(self, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'"
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_fields = ['password', 'token', 'secret', 'credit_card']

    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Log the request if it's an API call
        if request.path.startswith('/api/'):
            self._log_request(request, response)
        
        return response

    def _log_request(self, request, response):
        # Get request details
        method = request.method
        path = request.path
        user = request.user if request.user.is_authenticated else None
        client_ip = self._get_client_ip(request)
        
        # Sanitize request data
        request_data = self._sanitize_data(self._get_request_data(request))
        
        # Create audit log entry
        from security.models import AuditLog
        AuditLog.objects.create(
            user=user,
            method=method,
            path=path,
            request_data=request_data,
            response_status=response.status_code,
            ip_address=client_ip
        )

    def _get_request_data(self, request):
        if request.method == 'GET':
            return dict(request.GET)
        
        if request.content_type == 'application/json':
            try:
                return json.loads(request.body)
            except json.JSONDecodeError:
                return {}
                
        return dict(request.POST)

    def _sanitize_data(self, data):
        """Remove sensitive information from request data"""
        if isinstance(data, dict):
            return {
                k: '******' if any(field in k.lower() for field in self.sensitive_fields)
                else self._sanitize_data(v)
                for k, v in data.items()
            }
        if isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        return data

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
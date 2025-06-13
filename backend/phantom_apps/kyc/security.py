# backend/phantom_apps/kyc/security.py

import hashlib
import hmac
import secrets
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class KYCSecurityMiddleware:
    """Security middleware for KYC operations"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Rate limiting for KYC endpoints
        if request.path.startswith('/api/kyc/'):
            if not self.check_rate_limit(request):
                return HttpResponseForbidden("Rate limit exceeded")
        
        response = self.get_response(request)
        return response
    
    def check_rate_limit(self, request):
        """Implement rate limiting for KYC endpoints"""
        client_ip = self.get_client_ip(request)
        
        # Different limits for different endpoints
        if 'start_verification' in request.path:
            return self.rate_limit(f"kyc_start_{client_ip}", 5, 3600)  # 5 attempts per hour
        elif 'webhook' in request.path:
            return self.rate_limit(f"webhook_{client_ip}", 100, 60)  # 100 per minute
        else:
            return self.rate_limit(f"kyc_general_{client_ip}", 60, 300)  # 60 per 5 minutes
    
    def rate_limit(self, key, limit, window):
        """Generic rate limiting function"""
        current = cache.get(key, 0)
        if current >= limit:
            return False
        
        cache.set(key, current + 1, window)
        return True
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class KYCDataEncryption:
    """Encryption utilities for sensitive KYC data"""
    
    @staticmethod
    def encrypt_sensitive_data(data):
        """Encrypt sensitive data before storage"""
        # Implementation depends on your encryption library
        # Example using Django's signing framework
        from django.core.signing import Signer
        signer = Signer()
        return signer.sign(data)
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data):
        """Decrypt sensitive data"""
        from django.core.signing import Signer, BadSignature
        signer = Signer()
        try:
            return signer.unsign(encrypted_data)
        except BadSignature:
            logger.error("Failed to decrypt sensitive data")
            return None
    
    @staticmethod
    def hash_document_number(doc_number):
        """Hash document numbers for privacy"""
        salt = settings.SECRET_KEY[:16]  # Use part of secret key as salt
        return hashlib.pbkdf2_hmac('sha256', doc_number.encode(), salt.encode(), 100000).hex()


class WebhookSignatureValidator:
    """Validate webhook signatures for security"""
    
    @staticmethod
    def validate_veriff_signature(payload, signature, secret):
        """Validate Veriff webhook signature"""
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def generate_webhook_secret():
        """Generate a secure webhook secret"""
        return secrets.token_urlsafe(32)

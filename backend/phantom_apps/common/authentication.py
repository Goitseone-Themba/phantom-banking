from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import logging

logger = logging.getLogger('phantom_apps')

class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT Authentication with logging"""
    
    def authenticate(self, request):
        try:
            result = super().authenticate(request)
            if result:
                user, token = result
                logger.info(f"User {user.username} authenticated via JWT")
            return result
        except AuthenticationFailed as e:
            logger.warning(f"JWT Authentication failed: {e}")
            raise

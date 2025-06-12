"""
Email and security settings that should be imported into the main Django settings.py
"""

import os
from datetime import timedelta

# Camunda BPM Settings
CAMUNDA_SETTINGS = {
    'REST_URL': os.getenv('CAMUNDA_REST_URL', 'http://localhost:8080/engine-rest'),
    'CLIENT_ID': os.getenv('CAMUNDA_CLIENT_ID', 'phantom-worker'),
    'CLIENT_MAX_TASKS': int(os.getenv('CAMUNDA_CLIENT_MAX_TASKS', '1')),
    'CLIENT_LOCK_DURATION': int(os.getenv('CAMUNDA_CLIENT_LOCK_DURATION', '10000')),  # 10 seconds
    'CLIENT_ASYNC_RESPONSE_TIMEOUT': int(os.getenv('CAMUNDA_CLIENT_ASYNC_RESPONSE_TIMEOUT', '5000')),  # 5 seconds
    'PROCESSES': {
        'WALLET_CREATION': 'wallet-creation-process',
        'KYC_VALIDATION': 'kyc-validation-process',
        'MERCHANT_APPROVAL': 'merchant-approval-process',
        'SUSPICIOUS_ACTIVITY': 'suspicious-activity-process',
        'EMAIL_VERIFICATION': 'email-verification-process'
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'mpheelebang@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'Garebantsi#4')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', 'your-secret-key'),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
    'TOKEN_USER_CLASS': 'security.models.CustomUser',
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Security Settings
SECURITY_SETTINGS = {
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOGIN_ATTEMPT_TIMEOUT': 30,  # minutes
    'PASSWORD_RESET_TIMEOUT': 60,  # minutes
    'EMAIL_VERIFICATION_TIMEOUT': 24 * 60,  # minutes (24 hours)
    'REQUIRE_EMAIL_VERIFICATION': True,
    'MERCHANT_APPROVAL_REQUIRED': True,
}

# Frontend URL for email links
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8000')
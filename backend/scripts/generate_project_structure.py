#!/usr/bin/env python3
"""
Phantom Banking Project Structure Generator with PostgreSQL Integration
Creates the complete Django project structure without overriding existing files
"""

import os
import sys
from pathlib import Path

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {path}")
    else:
        print(f"⏭️  Directory exists, skipping: {path}")

def create_file(file_path, content):
    """Create file with content if it doesn't exist"""
    if not file_path.exists():
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Created file: {file_path}")
    else:
        print(f"⏭️  File exists, skipping: {file_path}")

def main():
    print("🏦 Phantom Banking - PostgreSQL Integrated Project Structure Generator")
    print("=" * 80)
    
    # Get current directory
    base_dir = Path.cwd()
    print(f"📂 Base directory: {base_dir}")
    
    # Main project directories
    directories = [
        # Core Django project
        "core",
        
        # Core Django apps
        "phantom_apps",
        "phantom_apps/merchants",
        "phantom_apps/customers", 
        "phantom_apps/wallets",
        "phantom_apps/transactions",
        "phantom_apps/common",
        "phantom_apps/common/management",
        "phantom_apps/common/management/commands",
        
        # Mock systems directory with two apps
        "phantom_apps/mock_systems",
        "phantom_apps/mock_systems/fnb",
        "phantom_apps/mock_systems/mobile_money",
        
        # API structure
        "api",
        "api/v1",
        
        # Scripts directory
        "scripts",
        
        # Tests directory with component tests
        "tests",
        "tests/components",
        "tests/fixtures",
        
        # Media and static
        "media",
        "media/kyc_documents",
        "media/qr_codes",
        "static",
        "logs",
        
        # Templates
        "templates",
    ]
    
    # Create directories
    print("\n📁 Creating directories...")
    for directory in directories:
        create_directory(base_dir / directory)
    
    # Python package __init__.py files
    init_files = [
        "core/__init__.py",
        "phantom_apps/__init__.py",
        "phantom_apps/merchants/__init__.py",
        "phantom_apps/customers/__init__.py",
        "phantom_apps/wallets/__init__.py", 
        "phantom_apps/transactions/__init__.py",
        "phantom_apps/common/__init__.py",
        "phantom_apps/common/management/__init__.py",
        "phantom_apps/common/management/commands/__init__.py",
        "phantom_apps/mock_systems/__init__.py",
        "phantom_apps/mock_systems/fnb/__init__.py",
        "phantom_apps/mock_systems/mobile_money/__init__.py",
        "api/__init__.py",
        "api/v1/__init__.py",
        "tests/__init__.py",
        "tests/components/__init__.py",
    ]
    
    print("\n📦 Creating Python package files...")
    for init_file in init_files:
        create_file(base_dir / init_file, "")
    
    # Core Django project files
    core_files = {
        "core/settings.py": '''import environ
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    USE_SQLITE=(bool, False),
    DB_POOL_MIN_CONN=(int, 1),
    DB_POOL_MAX_CONN=(int, 20),
    DB_POOL_TIMEOUT=(int, 30),
    HEALTH_CHECK_ENABLED=(bool, True),
)

# Read .env file
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_extensions',
]

# Add debug toolbar only in development
if DEBUG:
    THIRD_PARTY_APPS.append('debug_toolbar')

LOCAL_APPS = [
    'phantom_apps.merchants',
    'phantom_apps.wallets', 
    'phantom_apps.transactions',
    'phantom_apps.customers',
    'phantom_apps.common',
    
    # Mock Systems (separate apps)
    'phantom_apps.mock_systems.fnb',
    'phantom_apps.mock_systems.mobile_money',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add debug toolbar middleware only in development
if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database Configuration with Connection Pooling
USE_SQLITE = env.bool('USE_SQLITE', False)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,
                'check_same_thread': False,  # Django 5.2+ SQLite optimization
            }
        }
    }
else:
    # PostgreSQL configuration with psycopg3 support
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='phantom_banking_dev'),
            'USER': env('DB_USER', default='phantom_dev'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'OPTIONS': {
                'connect_timeout': env('DB_POOL_TIMEOUT', default=30),
                'options': '-c default_transaction_isolation=read_committed',
                # Psycopg3 optimizations
                'server_side_binding': True,
            },
            'CONN_MAX_AGE': 600,  # Increased for Django 5.2+
            'CONN_HEALTH_CHECKS': True,
            'ATOMIC_REQUESTS': True,
            'TEST': {
                'NAME': 'test_phantom_banking_dev',
                'CHARSET': 'utf8',
            },
        }
    }

# Database Connection Retry Configuration
DATABASE_CONNECTION_RETRY = {
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 2,  # seconds
    'BACKOFF_FACTOR': 1.5,
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Gaborone' 
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) - Django 5.2+ configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static files storage (Django 5.2+ with WhiteNoise)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework Configuration - Updated for latest DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'phantom_apps.common.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# JWT Configuration - Updated for latest simplejwt
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'phantom-banking-api',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# API Documentation - Updated for latest drf-spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'Phantom Banking API',
    'DESCRIPTION': 'Embedded Accounts for the Unbanked - FNB Hackathon 2025',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
    ],
    'SECURITY': [
        {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
    ],
    'AUTHENTICATION_WHITELIST': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'TAGS': [
        {'name': 'Authentication', 'description': 'JWT authentication endpoints'},
        {'name': 'Merchants', 'description': 'Merchant management'},
        {'name': 'Customers', 'description': 'Customer management'},
        {'name': 'Wallets', 'description': 'Phantom wallet operations'},
        {'name': 'Transactions', 'description': 'Payment processing'},
        {'name': 'Health', 'description': 'System health checks'},
    ],
}

# CORS Settings - Updated configuration
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:5173',  # Vite default
    'http://127.0.0.1:5173',
])

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in development

# Additional CORS headers for better API support
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Redis Configuration for Sessions and Cache
REDIS_URL = env('REDIS_URL', default='redis://127.0.0.1:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': env('REDIS_MAX_CONNECTIONS', default=50),
                'retry_on_timeout': True,
                'health_check_interval': 30,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'TIMEOUT': 300,
        'KEY_PREFIX': 'phantom_banking',
        'VERSION': 1,
    }
}

# Session Configuration using Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Custom Business Settings
PHANTOM_BANKING_SETTINGS = {
    'WALLET_DAILY_LIMIT': float(env('PHANTOM_WALLET_DAILY_LIMIT', default=50000.00)),
    'WALLET_MONTHLY_LIMIT': float(env('PHANTOM_WALLET_MONTHLY_LIMIT', default=200000.00)),
    'DEFAULT_CURRENCY': env('DEFAULT_CURRENCY', default='BWP'),
    'DEFAULT_TRANSACTION_FEE': float(env('DEFAULT_TRANSACTION_FEE', default=0.50)),
    'MOCK_FNB_BASE_URL': env('MOCK_FNB_BASE_URL', default='http://localhost:8000/api/v1/mock-fnb'),
    'MOCK_FNB_API_KEY': env('MOCK_FNB_API_KEY', default='dev_key'),
    'MOCK_FNB_API_SECRET': env('MOCK_FNB_API_SECRET', default='dev_secret'),
}

# Logging Configuration - Enhanced for Django 5.2+
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}"}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'phantom_banking.log',
            'formatter': 'verbose',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'phantom_banking_errors.log',
            'formatter': 'json',
            'maxBytes': 5242880,  # 5MB
            'backupCount': 3,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'phantom_banking': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'phantom_apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Security Settings for Production - Django 5.2+ enhanced security
if not DEBUG:
    # HTTPS Settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_PRELOAD = True
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookie Security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
    
    # Additional Security Headers
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Debug Toolbar Configuration (Django 5.2+ compatible)
if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Debug Toolbar Panels
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]
    
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }

# Email Configuration for Django 5.2+
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
if not DEBUG:
    EMAIL_HOST = env('EMAIL_HOST', default='')
    EMAIL_PORT = env('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@phantombanking.com')

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Performance Settings for Django 5.2+
if not DEBUG:
    # Enable template caching
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# Custom Settings Validation
PHANTOM_BANKING_VERSION = '1.0.0'
PHANTOM_BANKING_API_VERSION = 'v1'
''',

        "core/urls.py": '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

def health_check(request):
    """Basic health check endpoint"""
    return JsonResponse({
        'status': 'healthy', 
        'service': 'phantom-banking',
        'version': '1.0.0',
        'django_version': '5.2+',
        'api_version': 'v1'
    })

def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        'api': 'Phantom Banking API',
        'version': '1.0.0',
        'description': 'Embedded Accounts for the Unbanked - FNB Hackathon 2025',
        'documentation': '/api/docs/',
        'health_check': '/health/',
        'admin': '/admin/',
        'endpoints': {
            'authentication': '/api/v1/auth/',
            'merchants': '/api/v1/merchants/',
            'customers': '/api/v1/customers/',
            'wallets': '/api/v1/wallets/',
            'transactions': '/api/v1/transactions/',
            'health': '/api/v1/health/',
        }
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health checks and info
    path('health/', health_check, name='health_check'),
    path('', api_info, name='api_info'),
    
    # JWT Authentication - Enhanced for Django 5.2+
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API endpoints
    path('api/v1/', include('api.v1.urls')),
    
    # API Documentation - Updated for latest drf-spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Development-specific URLs
if settings.DEBUG:
    # Static and media files for development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar (Django 5.2+ compatible)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        urlpatterns = [
            path('__debug__/', include('debug_toolbar.urls')),
        ] + urlpatterns

# Admin customization for Phantom Banking
admin.site.site_header = "Phantom Banking Admin"
admin.site.site_title = "Phantom Banking"
admin.site.index_title = "Welcome to Phantom Banking Administration"
admin.site.site_url = "/api/docs/"  # Link to API docs from admin
''',

        "core/wsgi.py": '''"""
WSGI config for Phantom Banking project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
''',

        "manage.py": '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
''',
    }
    
    print("\n🔧 Creating core Django project files...")
    for file_path, content in core_files.items():
        create_file(base_dir / file_path, content)
    
    # Django app files with JWT integration
    app_files = {
        # Common app with JWT authentication views
        "phantom_apps/common/authentication.py": '''from rest_framework_simplejwt.authentication import JWTAuthentication
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
''',

        "phantom_apps/common/permissions.py": '''from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsMerchantOwner(BasePermission):
    """
    Custom permission to only allow merchants to access their own data.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a merchant attribute and if it matches the user
        if hasattr(obj, 'merchant'):
            return obj.merchant.user == request.user
        return False

class IsWalletOwner(BasePermission):
    """
    Custom permission to only allow wallet owners to access their wallets.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a customer or merchant relationship
        if hasattr(obj, 'customer') and hasattr(obj.customer, 'merchant'):
            return obj.customer.merchant.user == request.user
        return False
''',

        "phantom_apps/common/exceptions.py": '''from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('phantom_apps')

def custom_exception_handler(exc, context):
    """
    Custom exception handler for better error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the exception
        logger.error(f"API Exception: {exc} - Context: {context}")
        
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code,
            'details': response.data if isinstance(response.data, dict) else {}
        }
        
        response.data = custom_response_data
    
    return response

class PhantomBankingException(Exception):
    """Base exception for Phantom Banking operations"""
    pass

class WalletException(PhantomBankingException):
    """Exception for wallet-related operations"""
    pass

class TransactionException(PhantomBankingException):
    """Exception for transaction-related operations"""
    pass

class PaymentChannelException(PhantomBankingException):
    """Exception for payment channel operations"""
    pass
''',

        # Merchants app with JWT
        "phantom_apps/merchants/models.py": '''from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Merchant(models.Model):
    """Merchant model for businesses using Phantom Banking"""
    
    merchant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant')
    business_name = models.CharField(max_length=255)
    fnb_account_number = models.CharField(max_length=20, unique=True)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    business_registration = models.CharField(max_length=50, unique=True)
    
    # API credentials
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    api_secret_hash = models.CharField(max_length=128, blank=True)
    
    # Status and metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Business settings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.50)
    webhook_url = models.URLField(blank=True, null=True)
    
    class Meta:
        db_table = 'merchants'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.business_name

class APICredential(models.Model):
    """API credentials for merchant authentication"""
    
    credential_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='credentials')
    api_key = models.CharField(max_length=64, unique=True)
    api_secret_hash = models.CharField(max_length=128)
    permissions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_credentials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.merchant.business_name} - {self.api_key[:8]}..."
''',

        "phantom_apps/merchants/serializers.py": '''from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Merchant, APICredential

class MerchantRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for merchant registration"""
    
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Merchant
        fields = [
            'username', 'password', 'password_confirm',
            'business_name', 'fnb_account_number', 
            'contact_email', 'phone_number', 'business_registration',
            'webhook_url'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        # Extract user data
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=validated_data['contact_email'],
            password=password
        )
        
        # Create merchant
        merchant = Merchant.objects.create(user=user, **validated_data)
        return merchant

class MerchantSerializer(serializers.ModelSerializer):
    """Serializer for merchant data"""
    
    class Meta:
        model = Merchant
        fields = [
            'merchant_id', 'business_name', 'fnb_account_number',
            'contact_email', 'phone_number', 'business_registration',
            'created_at', 'is_active', 'commission_rate', 'webhook_url'
        ]
        read_only_fields = ['merchant_id', 'created_at']

class APICredentialSerializer(serializers.ModelSerializer):
    """Serializer for API credentials"""
    
    class Meta:
        model = APICredential
        fields = [
            'credential_id', 'api_key', 'permissions',
            'created_at', 'expires_at', 'is_active', 'last_used_at'
        ]
        read_only_fields = ['credential_id', 'api_key', 'created_at', 'last_used_at']
''',

        "phantom_apps/merchants/views.py": '''from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from .models import Merchant, APICredential
from .serializers import MerchantRegistrationSerializer, MerchantSerializer, APICredentialSerializer
import logging

logger = logging.getLogger('phantom_apps')

class MerchantViewSet(viewsets.ModelViewSet):
    """ViewSet for merchant operations"""
    
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter merchants by authenticated user"""
        return Merchant.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """Register a new merchant"""
        serializer = MerchantRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            merchant = serializer.save()
            logger.info(f"New merchant registered: {merchant.business_name}")
            return Response({
                'message': 'Merchant registered successfully',
                'merchant_id': merchant.merchant_id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get merchant dashboard data"""
        try:
            merchant = request.user.merchant
            # Add dashboard logic here
            dashboard_data = {
                'merchant': MerchantSerializer(merchant).data,
                'total_wallets': 0,  # Add wallet count
                'total_transactions': 0,  # Add transaction count
                'total_volume': 0,  # Add transaction volume
            }
            return Response(dashboard_data)
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'Merchant not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def generate_api_credentials(self, request):
        """Generate new API credentials for merchant"""
        try:
            merchant = request.user.merchant
            # Add API credential generation logic here
            return Response({
                'message': 'API credentials generated successfully'
            })
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'Merchant not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
''',

        "phantom_apps/merchants/urls.py": '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MerchantViewSet

router = DefaultRouter()
router.register(r'', MerchantViewSet, basename='merchants')

app_name = 'merchants'

urlpatterns = [
    path('', include(router.urls)),
]
''',

        "phantom_apps/merchants/apps.py": '''from django.apps import AppConfig

class MerchantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.merchants'
    verbose_name = 'Merchants'
''',

        "phantom_apps/merchants/admin.py": '''from django.contrib import admin
from .models import Merchant, APICredential

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'contact_email', 'phone_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['business_name', 'contact_email', 'business_registration']
    readonly_fields = ['merchant_id', 'created_at', 'updated_at']

@admin.register(APICredential)
class APICredentialAdmin(admin.ModelAdmin):
    list_display = ['merchant', 'api_key', 'is_active', 'created_at', 'last_used_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['credential_id', 'created_at']
''',

        # Customers app
        "phantom_apps/customers/models.py": '''from django.db import models
from django.utils import timezone
import uuid

class Customer(models.Model):
    """Customer model for phantom wallet users"""
    
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='customers')
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    identity_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Status and metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    is_verified = models.BooleanField(default=False)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    nationality = models.CharField(max_length=50, default='BW')
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        unique_together = ['merchant', 'phone_number']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
''',

        "phantom_apps/customers/serializers.py": '''from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer data"""
    
    class Meta:
        model = Customer
        fields = [
            'customer_id', 'first_name', 'last_name', 
            'phone_number', 'email', 'identity_number',
            'created_at', 'status', 'is_verified',
            'preferred_language', 'nationality'
        ]
        read_only_fields = ['customer_id', 'created_at']

class CustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating customers"""
    
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'phone_number', 
            'email', 'identity_number', 'preferred_language', 'nationality'
        ]
    
    def create(self, validated_data):
        # Get merchant from request context
        merchant = self.context['request'].user.merchant
        return Customer.objects.create(merchant=merchant, **validated_data)
''',

        "phantom_apps/customers/views.py": '''from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Customer
from .serializers import CustomerSerializer, CustomerCreateSerializer
from ..common.permissions import IsMerchantOwner
import logging

logger = logging.getLogger('phantom_apps')

class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for customer operations"""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter customers by merchant"""
        try:
            return Customer.objects.filter(merchant=self.request.user.merchant)
        except:
            return Customer.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerCreateSerializer
        return CustomerSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new customer"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            logger.info(f"New customer created: {customer.first_name} {customer.last_name}")
            return Response(
                CustomerSerializer(customer).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
''',

        "phantom_apps/customers/urls.py": '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet

router = DefaultRouter()
router.register(r'', CustomerViewSet, basename='customers')

app_name = 'customers'

urlpatterns = [
    path('', include(router.urls)),
]
''',

        "phantom_apps/customers/apps.py": '''from django.apps import AppConfig

class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.customers'
    verbose_name = 'Customers'
''',

        "phantom_apps/customers/admin.py": '''from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'merchant', 'status', 'created_at']
    list_filter = ['status', 'is_verified', 'created_at', 'merchant']
    search_fields = ['first_name', 'last_name', 'phone_number', 'email']
    readonly_fields = ['customer_id', 'created_at', 'updated_at']
''',

        # API v1 URLs
        "api/v1/urls.py": '''from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Core business endpoints
    path('merchants/', include('phantom_apps.merchants.urls')),
    path('customers/', include('phantom_apps.customers.urls')),
    path('wallets/', include('phantom_apps.wallets.urls')),
    path('transactions/', include('phantom_apps.transactions.urls')),
    
    # Mock systems
    path('mock-fnb/', include('phantom_apps.mock_systems.fnb.urls')),
    path('mock-mobile-money/', include('phantom_apps.mock_systems.mobile_money.urls')),
    
    # Common utilities
    path('', include('phantom_apps.common.urls')),
]
''',

        # Common utilities
        "phantom_apps/common/views.py": '''from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import connection
from django.conf import settings
import time
import logging

logger = logging.getLogger('phantom_apps')

class HealthCheckView(APIView):
    """Basic health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'phantom-banking-api',
            'version': '1.0.0',
            'timestamp': time.time()
        })

class DatabaseHealthView(APIView):
    """Database connectivity check"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 as health_check")
                result = cursor.fetchone()
            
            connection_time = time.time() - start_time
            
            return Response({
                'database': {
                    'status': 'healthy',
                    'connection_time_ms': round(connection_time * 1000, 2),
                    'engine': settings.DATABASES['default']['ENGINE'],
                }
            })
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return Response({
                'database': {
                    'status': 'unhealthy',
                    'error': str(e)
                }
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
''',

        "phantom_apps/common/urls.py": '''from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('health/database/', views.DatabaseHealthView.as_view(), name='database_health'),
]
''',

        "phantom_apps/common/apps.py": '''from django.apps import AppConfig

class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.common'
    verbose_name = 'Common Utilities'
''',

        "phantom_apps/common/admin.py": '''from django.contrib import admin

# Common admin configurations will be defined here
''',

        # Basic model files for other apps
        "phantom_apps/wallets/models.py": '''from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class Wallet(models.Model):
    """Phantom wallet model"""
    
    wallet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE, related_name='wallet')
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='wallets')
    
    # Balance and currency
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='BWP')
    
    # Limits
    daily_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('50000.00'))
    monthly_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('200000.00'))
    
    # Status and metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    is_frozen = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'wallets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Wallet {self.wallet_id} - {self.customer.first_name} {self.customer.last_name}"
''',

        "phantom_apps/wallets/apps.py": '''from django.apps import AppConfig

class WalletsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.wallets'
    verbose_name = 'Wallets'
''',

        "phantom_apps/wallets/urls.py": '''from django.urls import path

app_name = 'wallets'

urlpatterns = [
    # Wallet URLs will be defined here
]
''',

        "phantom_apps/transactions/models.py": '''from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class Transaction(models.Model):
    """Transaction model for all payment operations"""
    
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('transfer', 'Transfer'),
    ]
    
    PAYMENT_CHANNELS = [
        ('qr_code', 'QR Code'),
        ('eft', 'EFT'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.CASCADE, related_name='transactions')
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BWP')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    payment_channel = models.CharField(max_length=20, choices=PAYMENT_CHANNELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # References and descriptions
    reference_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    external_reference = models.CharField(max_length=100, blank=True)
    
    # Fees and reconciliation
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_reconciled = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Failure information
    failure_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['merchant', 'created_at']),
            models.Index(fields=['wallet', 'created_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.reference_number} - {self.amount} {self.currency}"
''',

        "phantom_apps/transactions/apps.py": '''from django.apps import AppConfig

class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.transactions'
    verbose_name = 'Transactions'
''',

        "phantom_apps/transactions/urls.py": '''from django.urls import path

app_name = 'transactions'

urlpatterns = [
    # Transaction URLs will be defined here
]
''',

        # Mock FNB app
        "phantom_apps/mock_systems/fnb/models.py": '''from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class MockFNBAccount(models.Model):
    """Mock FNB account for development and testing"""
    
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_number = models.CharField(max_length=20, unique=True)
    account_holder_name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='BWP')
    
    # Account status
    is_active = models.BooleanField(default=True)
    account_type = models.CharField(max_length=20, default='savings')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mock_fnb_accounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"FNB Account {self.account_number} - {self.account_holder_name}"

class MockFNBTransaction(models.Model):
    """Mock FNB transaction for testing"""
    
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(MockFNBAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'mock_fnb_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"FNB Transaction {self.reference} - {self.amount}"
''',

        "phantom_apps/mock_systems/fnb/apps.py": '''from django.apps import AppConfig

class FnbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.mock_systems.fnb'
    verbose_name = 'Mock FNB System'
''',

        "phantom_apps/mock_systems/fnb/urls.py": '''from django.urls import path

app_name = 'mock_fnb'

urlpatterns = [
    # Mock FNB URLs will be defined here
]
''',

        # Mock Mobile Money app
        "phantom_apps/mock_systems/mobile_money/models.py": '''from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class MockMobileMoneyAccount(models.Model):
    """Mock mobile money account for development"""
    
    PROVIDERS = [
        ('orange', 'Orange Money'),
        ('mascom', 'Mascom MyZaka'),
        ('btc', 'BTC Smega'),
    ]
    
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True)
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Account status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mock_mobile_money_accounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_provider_display()} - {self.phone_number}"
''',

        "phantom_apps/mock_systems/mobile_money/apps.py": '''from django.apps import AppConfig

class MobileMoneyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phantom_apps.mock_systems.mobile_money'
    verbose_name = 'Mock Mobile Money System'
''',

        "phantom_apps/mock_systems/mobile_money/urls.py": '''from django.urls import path

app_name = 'mock_mobile_money'

urlpatterns = [
    # Mock Mobile Money URLs will be defined here
]
''',
    }
    
    print("\n📄 Creating Django app files...")
    for file_path, content in app_files.items():
        create_file(base_dir / file_path, content)
    
    # Create requirements.txt
    requirements_content = '''# Django and core dependencies
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0

# Database
psycopg2-binary==2.9.9

# Environment and configuration
django-environ==0.11.2

# API and documentation
drf-spectacular==0.26.5
django-cors-headers==4.3.1

# Redis and caching
django-redis==5.4.0
redis==5.0.1

# Development tools
django-extensions==3.2.3

# Testing
pytest==7.4.3
pytest-django==4.7.0
factory-boy==3.3.0

# Utilities
Pillow==10.1.0
celery==5.3.4

# Production
gunicorn==21.2.0
'''
    
    create_file(base_dir / "requirements.txt", requirements_content)
    
    # Create .env.example
    env_example_content = '''# Django Configuration
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
USE_SQLITE=False
DB_NAME=phantom_banking_dev
DB_USER=phantom_dev
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Database Connection Pool Settings
DB_POOL_MIN_CONN=1
DB_POOL_MAX_CONN=20
DB_POOL_TIMEOUT=30

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1
REDIS_MAX_CONNECTIONS=50

# API Configuration
API_VERSION=v1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080

# Business Rules
PHANTOM_WALLET_DAILY_LIMIT=50000.00
PHANTOM_WALLET_MONTHLY_LIMIT=200000.00
DEFAULT_CURRENCY=BWP
DEFAULT_TRANSACTION_FEE=0.50

# Mock FNB API Settings (for development)
MOCK_FNB_BASE_URL=http://localhost:8000/api/v1/mock-fnb
MOCK_FNB_API_KEY=dev_fnb_key_12345
MOCK_FNB_API_SECRET=dev_fnb_secret_67890

# Health Check Settings
HEALTH_CHECK_ENABLED=True
'''
    
    create_file(base_dir / ".env.example", env_example_content)
    
    # Create .env file (copy of example for development)
    create_file(base_dir / ".env", env_example_content)
    
    # Create gitignore
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Database
*.sqlite3
*.db

# Redis
dump.rdb

# Logs
logs/
*.log

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Celery
celerybeat-schedule
celerybeat.pid

# Node (if using frontend tools)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Backup files
*.bak
*.backup
'''
    
    create_file(base_dir / ".gitignore", gitignore_content)
    
    print("\n🎉 PostgreSQL-integrated project structure generation complete!")
    print("\n📋 Next steps:")
    print("1. Install PostgreSQL: sudo pacman -S postgresql")
    print("2. Initialize PostgreSQL: sudo -iu postgres initdb -D /var/lib/postgres/data")
    print("3. Start PostgreSQL: sudo systemctl start postgresql")
    print("4. Run database setup script: python scripts/setup_database.py")
    print("5. Install Python dependencies: pip install -r requirements.txt")
    print("6. Run migrations: python manage.py migrate")
    print("7. Test the setup: python scripts/test_migrations.py")
    print("8. Create superuser: python manage.py createsuperuser")
    print("9. Run server: python manage.py runserver")
    print("\n🚀 Ready for FNB Hackathon 2025 development!")

if __name__ == "__main__":
    main()
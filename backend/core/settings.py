import environ
import os
from pathlib import Path
from datetime import timedelta
from decimal import Decimal

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
    # 'drf_ysg',
]

# Add debug toolbar only in development
if DEBUG:
    THIRD_PARTY_APPS.append('debug_toolbar')

LOCAL_APPS = [

    # 'security.apps.SecuirtyConfig',
    'phantom_apps.merchants',
    'phantom_apps.wallets', 
    'phantom_apps.transactions',
    'phantom_apps.customers',
    'phantom_apps.common',
    'phantom_apps.kyc',
    'phantom_apps.monitoring',

    # 'phantom_apps.payments',
    # 'phantom_apps.kyc',

    # Mock Systems (separate apps)
    'phantom_apps.mock_systems.fnb',
    'phantom_apps.mock_systems.mobile_money',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    # 'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'phantom_apps.monitoring.middleware.PrometheusMetricsMiddleware',
    'phantom_apps.monitoring.middleware.DatabaseMetricsMiddleware',
    # 'security.middleware.SecurityHeadersMiddleware',
    # 'security.middleware.RequestLoggingMiddleware',
]

# Add debug toolbar middleware only in development
if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'phantom_apps', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
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
                # 'options': '-c default_transaction_isolation=read committed',  # Commented out to fix connection error
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
    os.path.join(BASE_DIR, 'phantom_apps', 'monitoring', 'static'),
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
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
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

CORS_ALLOW_CREDENTIALS = True #Only in development
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

# Payment System Configuration
PHANTOM_PAYMENTS = {
    'BASE_URL': os.getenv('BASE_URL', 'http://localhost:8000'),
    
    # QR Code Settings
    'QR_CODE': {
        'DEFAULT_EXPIRY_MINUTES': 15,
        'MAX_EXPIRY_MINUTES': 1440,  # 24 hours
        'IMAGE_SIZE': 300,
        'ERROR_CORRECTION': 'L',  # Low, Medium, Quartile, High
    },
    
    # EFT Settings
    'EFT': {
        'DEFAULT_TIMEOUT': 30,  # seconds
        'RETRY_ATTEMPTS': 3,
        'WEBHOOK_TIMEOUT': 10,
        'WEBHOOK_RETRY_DELAY': 5,
    },
    
    # Transaction Settings
    'TRANSACTIONS': {
        'DEFAULT_CURRENCY': 'BWP',
        'MAX_AMOUNT': Decimal('1000000.00'),
        'MIN_AMOUNT': Decimal('0.01'),
        'DEFAULT_FEE': Decimal('2.00'),
        'AUTO_RECONCILE': True,
    },
    
    # Bank Configurations
    'BANKS': {
        'fnb': {
            'name': 'First National Bank',
            'api_url': os.getenv('FNB_API_URL', 'https://api.fnb.co.bw'),
            'api_key': os.getenv('FNB_API_KEY'),
            'webhook_secret': os.getenv('FNB_WEBHOOK_SECRET'),
            'min_amount': Decimal('10.00'),
            'max_amount': Decimal('50000.00'),
            'fee_rate': Decimal('0.02'),
            'timeout': 30,
        },
        'standard': {
            'name': 'Standard Bank',
            'api_url': os.getenv('STANDARD_API_URL', 'https://api.standardbank.co.bw'),
            'api_key': os.getenv('STANDARD_API_KEY'),
            'webhook_secret': os.getenv('STANDARD_WEBHOOK_SECRET'),
            'min_amount': Decimal('10.00'),
            'max_amount': Decimal('100000.00'),
            'fee_rate': Decimal('0.015'),
            'timeout': 30,
        },
        'barclays': {
            'name': 'Barclays Bank',
            'api_url': os.getenv('BARCLAYS_API_URL', 'https://api.barclays.co.bw'),
            'api_key': os.getenv('BARCLAYS_API_KEY'),
            'webhook_secret': os.getenv('BARCLAYS_WEBHOOK_SECRET'),
            'min_amount': Decimal('5.00'),
            'max_amount': Decimal('75000.00'),
            'fee_rate': Decimal('0.025'),
            'timeout': 30,
        },
        'nedbank': {
            'name': 'Nedbank',
            'api_url': os.getenv('NEDBANK_API_URL', 'https://api.nedbank.co.bw'),
            'api_key': os.getenv('NEDBANK_API_KEY'),
            'webhook_secret': os.getenv('NEDBANK_WEBHOOK_SECRET'),
            'min_amount': Decimal('10.00'),
            'max_amount': Decimal('75000.00'),
            'fee_rate': Decimal('0.02'),
            'timeout': 30,
        },
        'choppies': {
            'name': 'Choppies Bank',
            'api_url': os.getenv('CHOPPIES_API_URL', 'https://api.choppiesbank.co.bw'),
            'api_key': os.getenv('CHOPPIES_API_KEY'),
            'webhook_secret': os.getenv('CHOPPIES_WEBHOOK_SECRET'),
            'min_amount': Decimal('5.00'),
            'max_amount': Decimal('25000.00'),
            'fee_rate': Decimal('0.03'),
            'timeout': 30,
        },
    }
}

# Production payment configuration
if not DEBUG: PHANTOM_PAYMENTS.update({
    'BASE_URL': 'https://api.phantombanking.bw',
    'MOCK_BANK_APIS': False,
    'WEBHOOK_SIGNATURE_VALIDATION': True,
    'RATE_LIMITING': {
        'QR_CREATE': '60/hour',
        'EFT_INITIATE': '30/hour',
        'PAYMENT_PROCESS': '100/hour',
    }
})

# Veriff Configuration
VERIFF_API_KEY = os.getenv('VERIFF_API_KEY', '')
VERIFF_API_SECRET = os.getenv('VERIFF_API_SECRET', '')
VERIFF_BASE_URL = os.getenv('VERIFF_BASE_URL', 'https://stationapi.veriff.com')  # Use sandbox for testing
VERIFF_WEBHOOK_SECRET = os.getenv('VERIFF_WEBHOOK_SECRET', '')

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
            'format': '{levelname} {asctime} {module} {message}',
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

# Celery Configuration for Async Tasks
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Gaborone'

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


# Security Settings for Production
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

# Debug Toolbar Configuration
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

# Email Configuration
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

# Performance Settings
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
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    
    # Your apps
    'phantom_apps.customers',
    'phantom_apps.merchants', 
    'phantom_apps.wallets',
    'phantom_apps.transactions',
]

# Add DRF settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# Spectacular settings for API docs
SPECTACULAR_SETTINGS = {
    'TITLE': 'Phantom Banking Payment API',
    'DESCRIPTION': 'QR Code and EFT Payment Processing API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Base URL for QR codes
BASE_URL = 'http://localhost:8000'
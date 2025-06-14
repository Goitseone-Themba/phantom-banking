# Phantom Banking Authentication System

A comprehensive authentication system for Phantom Banking using Django Allauth and dj-rest-auth with email verification, security features, and user management.

## 🚀 Features

### Core Authentication
- **Custom User Model**: Extended Django user with business fields
- **Email-based Authentication**: Users login with email instead of username
- **JWT Token Authentication**: Secure token-based API authentication
- **Email Verification**: Mandatory email verification for new registrations
- **Password Security**: Strong password validation and reset functionality

### Security Features
- **Account Lockout**: Automatic lockout after failed login attempts
- **Login Attempt Tracking**: Monitor and log all login attempts
- **Session Management**: Track and manage user sessions across devices
- **IP Address Logging**: Track user login locations for security
- **User Agent Detection**: Identify device types and browsers

### User Management
- **Multiple User Types**: Customer, Merchant, Admin, Staff
- **Profile Management**: Extended user profiles with business information
- **Verification Status**: Email, phone, and business verification tracking
- **Terms and Privacy**: Track acceptance of terms and privacy policies

## 📁 Structure

```
phantom_apps/authentication/
├── models.py              # User models and authentication tables
├── serializers.py         # API serializers for authentication
├── views.py              # Authentication API endpoints
├── urls.py               # URL routing for auth endpoints
├── utils.py              # Helper functions and utilities
├── tasks.py              # Celery tasks for async email sending
├── signals.py            # Signal handlers for auth events
├── admin.py              # Django admin configuration
├── apps.py               # App configuration
└── templates/
    └── authentication/
        └── emails/       # Email templates
            ├── verify_email.html
            ├── verify_email.txt
            ├── password_reset.html
            ├── password_reset.txt
            ├── welcome.html
            └── welcome.txt
```

## 🛠️ Installation & Setup

### 1. Dependencies

The authentication system requires these packages (already in requirements.txt):

```bash
pip install django-allauth dj-rest-auth
```

### 2. Settings Configuration

Add to your Django settings:

```python
# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Installed Apps
INSTALLED_APPS = [
    # ... other apps
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'phantom_apps.authentication',
]

# Middleware
MIDDLEWARE = [
    # ... other middleware
    'allauth.account.middleware.AccountMiddleware',
]

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth Configuration
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',
}

# dj-rest-auth Configuration
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'phantom-auth'
JWT_AUTH_REFRESH_COOKIE = 'phantom-refresh'

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'phantom_apps.authentication.serializers.UserDetailsSerializer',
    'LOGIN_SERIALIZER': 'phantom_apps.authentication.serializers.LoginSerializer',
    # ... other serializers
}
```

### 3. Database Migration

**Important**: This authentication system uses a custom User model. If you have existing data:

```bash
# For new projects
python manage.py makemigrations authentication
python manage.py migrate

# For existing projects with data - see Migration Guide below
```

### 4. URL Configuration

Add to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other URLs
    path('api/v1/auth/', include('phantom_apps.authentication.urls')),
]
```

## 🔗 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/status/` - Check auth status

### Email Verification
- `POST /api/v1/auth/verify-email/` - Verify email with token
- `POST /api/v1/auth/resend-verification/` - Resend verification email

### Password Management
- `POST /api/v1/auth/password/change/` - Change password
- `POST /api/v1/auth/password/reset/` - Request password reset
- `POST /api/v1/auth/password/reset/confirm/` - Confirm password reset

### User Profile
- `GET /api/v1/auth/user/` - Get user details
- `PUT/PATCH /api/v1/auth/user/` - Update user details
- `GET/PUT/PATCH /api/v1/auth/profile/` - Get/update user profile

### Security
- `GET /api/v1/auth/login-attempts/` - View login attempts
- `GET /api/v1/auth/sessions/` - View active sessions
- `DELETE /api/v1/auth/sessions/` - Terminate session

## 📧 Email Configuration

The system sends emails for:
- Email verification
- Password reset
- Welcome messages

### Development (Console Backend)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production (SMTP)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@phantombanking.com'
```

## 🔐 Security Features

### Account Lockout
- Accounts are locked after 5 failed login attempts
- Lockout duration: 30 minutes (configurable)
- Automatic unlock after timeout

### Password Requirements
- Minimum 8 characters
- Must contain uppercase and lowercase letters
- Must contain at least one digit
- Must contain at least one special character

### Session Security
- JWT tokens with configurable expiry
- Refresh token rotation
- Session tracking across devices
- IP address logging

## 👥 User Types

### Customer
- Basic wallet users
- Can send/receive payments
- Basic verification requirements

### Merchant
- Business accounts
- Can accept payments
- Requires business verification
- API access for integrations

### Admin
- Full system access
- User management capabilities
- System configuration

### Staff
- Limited admin access
- Customer support functions
- Reporting access

## 🚀 Usage Examples

### Registration
```python
import requests

response = requests.post('http://localhost:8000/api/v1/auth/register/', {
    'email': 'user@example.com',
    'first_name': 'John',
    'last_name': 'Doe',
    'password': 'SecurePass123!',
    'password_confirm': 'SecurePass123!',
    'user_type': 'customer',
    'terms_accepted': True,
    'privacy_accepted': True
})
```

### Login
```python
response = requests.post('http://localhost:8000/api/v1/auth/login/', {
    'username': 'user@example.com',  # email is used as username
    'password': 'SecurePass123!'
})

# Extract JWT token from response
token = response.json()['access_token']
```

### Authenticated Requests
```python
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/v1/auth/user/', headers=headers)
```

## 🔧 Migration Guide for Existing Projects

If you have an existing project with user data:

### Option 1: Fresh Start (Recommended for Development)
```bash
# Backup existing data
pg_dump phantom_banking_dev > backup.sql

# Drop and recreate database
dropdb phantom_banking_dev
createdb phantom_banking_dev

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Option 2: Data Migration (Advanced)
```bash
# 1. Create custom migration to copy existing user data
python manage.py makemigrations --empty authentication

# 2. Edit the migration to copy data from auth.User to authentication.User
# 3. Update foreign keys in other models
# 4. Run migration
python manage.py migrate
```

## 🧪 Testing

Run authentication tests:
```bash
python manage.py test phantom_apps.authentication
```

## 📝 Admin Interface

The authentication system provides a comprehensive admin interface:

- **Users**: Manage user accounts, verification status, security settings
- **Email Verification Tokens**: View and manage verification tokens
- **Password Reset Tokens**: Monitor password reset requests
- **Login Attempts**: Security monitoring and login tracking
- **User Sessions**: Active session management

## 🔄 Async Tasks

The system uses Celery for async email sending:

```python
# Send verification email
from phantom_apps.authentication.tasks import send_verification_email
send_verification_email.delay(user_id)

# Send password reset email
from phantom_apps.authentication.tasks import send_password_reset_email
send_password_reset_email.delay(user_id, ip_address)
```

## 🛡️ Security Best Practices

1. **Use HTTPS in Production**: Always use SSL/TLS
2. **Secure JWT Cookies**: Enable httpOnly and secure flags
3. **Rate Limiting**: Implement API rate limiting
4. **CORS Configuration**: Properly configure CORS origins
5. **Monitor Login Attempts**: Set up alerts for suspicious activity
6. **Regular Token Rotation**: Use refresh token rotation
7. **Session Management**: Implement session timeout and cleanup

## 🐛 Troubleshooting

### Common Issues

1. **Migration Conflicts**
   - Issue: Custom user model conflicts with existing auth migrations
   - Solution: Follow migration guide above

2. **Email Not Sending**
   - Issue: Verification emails not delivered
   - Solution: Check email backend configuration and SMTP settings

3. **JWT Token Issues**
   - Issue: Token authentication failing
   - Solution: Verify JWT configuration and token headers

4. **Account Lockout**
   - Issue: Users locked out after failed attempts
   - Solution: Check lockout settings or unlock manually via admin

### Debug Mode

Enable debug logging:
```python
LOGGING = {
    'loggers': {
        'phantom_apps.authentication': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## 📞 Support

For issues related to the authentication system:
1. Check the troubleshooting section above
2. Review Django and Allauth documentation
3. Check system logs for error details
4. Verify configuration settings

---

**Note**: This authentication system is designed for the Phantom Banking platform. Adapt the configuration according to your specific requirements.


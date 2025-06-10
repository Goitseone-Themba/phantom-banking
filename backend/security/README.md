# Security Module Documentation

## Overview
The security module handles all authentication, authorization, and security-related functionality for the Phantom platform. It implements a robust security system with features including 2FA, email verification, and comprehensive audit logging.

## Key Components

### 1. Authentication System
- **Two-Factor Authentication (2FA)**
  - Implemented using TOTP (Time-based One-Time Password)
  - Google SMTP integration for OTP delivery
  - Backup codes generation for account recovery
  - Mandatory 2FA for all user logins

### 2. User Management (`models.py`)
- CustomUser model with extended security features
- Role-based access control (Admin, Merchant, Customer)
- Account locking mechanism after failed attempts
- Email verification system
- Password reset functionality
- API key management

### 3. Security Utilities (`auth_utils.py`)
- Email verification handling
- Password reset functionality
- Merchant user creation
- Login validation with 2FA support
- Token generation and verification

### 4. Audit and Monitoring
- Comprehensive audit logging system
- Security event tracking
- IP address monitoring
- Suspicious activity detection

### 5. Merchant Profile Management
- Business verification system
- Admin approval workflow
- Contact information management
- Registration number validation

## Security Features

### Authentication Flow
1. User submits login credentials
2. System validates username/email and password
3. If valid, generates and sends OTP via email
4. User must enter valid OTP to complete login
5. Session is established only after successful 2FA

### Account Protection
- Account lockout after 5 failed attempts
- 30-minute lockout duration
- Email notifications for security events
- IP address tracking
- User agent monitoring

### Email Security
- Secure email verification process
- Password reset with expiring tokens
- Google SMTP integration for reliable delivery
- HTML and plain text email support

### Data Protection
- Password hashing using Django's security best practices
- API key rotation
- Session management
- CSRF protection
- XSS prevention

## Configuration

### Google SMTP Settings
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-specific-password'
```

### Security Settings
```python
# Security timeouts
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour
EMAIL_VERIFICATION_TIMEOUT = 86400  # 24 hours
ACCOUNT_LOCKOUT_DURATION = 1800  # 30 minutes
MAX_FAILED_ATTEMPTS = 5

# 2FA settings
OTP_VALIDITY_PERIOD = 300  # 5 minutes
BACKUP_CODES_COUNT = 10
```

## API Endpoints

### Authentication Endpoints
- POST /api/auth/login/ - Initial login
- POST /api/auth/verify-2fa/ - 2FA verification
- POST /api/auth/reset-password/ - Password reset
- POST /api/auth/verify-email/ - Email verification

### User Management Endpoints
- POST /api/users/create/ - Create new user
- PUT /api/users/update/ - Update user details
- POST /api/users/enable-2fa/ - Enable 2FA
- GET /api/users/backup-codes/ - Generate backup codes

## Best Practices
1. Always validate email addresses
2. Implement rate limiting on sensitive endpoints
3. Use secure session management
4. Regular security audits
5. Monitor failed login attempts
6. Keep security dependencies updated
7. Regular backup code rotation
8. Implement proper error handling

## Error Handling
- Clear error messages without exposing sensitive information
- Proper logging of security events
- Graceful failure handling
- User notification for security events

## Future Enhancements
1. Hardware token support
2. Biometric authentication integration
3. Enhanced fraud detection
4. Geographic location validation
5. Real-time security monitoring dashboard

## Maintenance
- Regular security audits
- Log rotation and archival
- Token cleanup jobs
- Failed login attempt reset
- Expired session cleanup
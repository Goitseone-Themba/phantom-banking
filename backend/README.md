# Phantom Banking Backend

This directory contains the Django backend application for Phantom Banking, focusing on providing secure wallet solutions for unbanked populations.

## Key Modules

### 1. Security Module (`/security`)

The security module is the foundation of our authentication and authorization system.

#### Models (`security/models.py`)

- **CustomUser**: Our core user model that extends Django's AbstractBaseUser
  - Uses UUID primary keys for enhanced security
  - Implements role-based access control with roles: 'admin', 'merchant', 'customer'
  - Tracks login attempts and supports account locking
  - Fields:
    ```python
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    ```

- **CustomerUser**: Profile model for customers with personal information
  - One-to-one relationship with CustomUser
  - Stores KYC information
  - Fields:
    ```python
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    national_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20)
    ```

- **MerchantUser**: Profile model for merchants with business information
  - One-to-one relationship with CustomUser
  - Stores business verification details
  - Fields:
    ```python
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='merchant_profile')
    business_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    business_type = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    ```

- **SecuritySettings**: Stores security preferences and 2FA settings
  - One-to-one relationship with CustomUser
  - Manages API keys and backup codes
  - Fields:
    ```python
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='security_settings')
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    api_key = models.UUIDField(default=uuid.uuid4, editable=False)
    api_key_expires = models.DateTimeField(null=True, blank=True)
    ```

#### Authentication Views (`security/views.py`)

- **AuthViewSet**: Handles all authentication operations
  - `merchant_signup`: Registers new merchant accounts
  - `login`: Authenticates users and issues JWT tokens
  - `verify_email`: Verifies user email addresses
  - `request_password_reset`: Initiates password reset flow
  - `reset_password`: Completes password reset with token
  - `logout`: Invalidates refresh tokens

#### Middleware (`security/middleware.py`)

- **SecurityHeadersMiddleware**: Adds security headers to all responses
  - Content-Security-Policy
  - X-XSS-Protection
  - X-Content-Type-Options
  - Referrer-Policy

- **RequestLoggingMiddleware**: Logs all API requests for audit purposes
  - Records request method, path, IP address, and user agent
  - Logs response status code and timing information

#### Authentication Utilities (`security/auth_utils.py`)

- **Token Management**:
  - `create_tokens_for_user`: Creates access and refresh tokens
  - `verify_token`: Validates token authenticity and expiration

- **Password Management**:
  - `validate_password_strength`: Ensures passwords meet security requirements
  - `hash_password`: Securely hashes passwords
  - `verify_password`: Validates password against stored hash

- **Email Verification**:
  - `send_verification_email`: Sends email with verification token
  - `verify_email`: Validates email verification token

### 2. Wallets Module (`/wallets`)

The wallets module manages wallet creation, approval, and operations.

#### Models (`wallets/models.py`)

- **WalletCreationRequest**: Tracks requests to create new wallets
  - Created by merchants for their customers
  - Fields:
    ```python
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE, related_name='wallet_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    national_id = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    username = models.CharField(max_length=150, null=True, blank=True)
    ```

- **Wallet**: Represents a customer's wallet
  - Linked to both customer and merchant
  - Tracks balance and transaction limits
  - Fields:
    ```python
    wallet_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='wallets')
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.PROTECT, related_name='wallets')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPE_CHOICES, default='basic')
    daily_transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('1000.00'))
    monthly_transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('10000.00'))
    ```

- **WalletAuditLog**: Records all actions performed on wallets
  - Maintains audit trail for compliance and security
  - Fields:
    ```python
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()
    ip_address = models.GenericIPAddressField()
    ```

#### Views (`wallets/views.py`)

- **WalletViewSet**: Manages wallet operations
  - `get_queryset`: Filters wallets based on user role
  - List, retrieve, update operations with proper permissions

- **WalletCreationRequestViewSet**: Handles wallet creation flow
  - `create`: Creates new wallet requests
  - `approve`: Approves requests and creates wallets
  - `reject`: Rejects wallet creation requests
  - `_send_password_email`: Sends credentials to new customers

#### Key Methods

- **Wallet Creation Flow**:
  1. Merchant creates a wallet request
  2. System validates customer data
  3. Admin approves the request
  4. System creates user account with random password
  5. System creates wallet and links to customer
  6. Customer receives credentials via email

- **Transaction Validation**:
  ```python
  def is_transaction_allowed(self, amount):
      if self.status != 'active':
          return False, "Wallet is not active"
          
      if amount > self.balance:
          return False, "Insufficient funds"
          
      if (self.daily_transaction_amount + amount) > self.daily_transaction_limit:
          return False, "Daily transaction limit exceeded"
          
      if (self.monthly_transaction_amount + amount) > self.monthly_transaction_limit:
          return False, "Monthly transaction limit exceeded"
          
      return True, "Transaction allowed"
  ```

### 3. Merchants Module (`/phantom_apps/merchants`)

The merchants module manages merchant accounts and their API access.

#### Models (`phantom_apps/merchants/models.py`)

- **Merchant**: Represents a business entity
  - Linked to a MerchantUser profile
  - Fields:
    ```python
    merchant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(max_length=255)
    fnb_account_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    registration_number = models.CharField(max_length=100, unique=True)
    admin_name = models.CharField(max_length=255)
    admin_email = models.EmailField()
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='merchant')
    ```

- **APICredential**: Manages API access for merchants
  - Securely stores API keys and permissions
  - Fields:
    ```python
    credential_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='credentials')
    api_key = models.CharField(max_length=64, unique=True)
    api_secret_hash = models.CharField(max_length=128)
    permissions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    ```

#### Views (`phantom_apps/merchants/views.py`)

- **MerchantViewSet**: Manages merchant operations
  - `get_queryset`: Filters merchants based on user permissions
  - `create_wallet`: Endpoint for merchants to create customer wallets
  - `get_transactions`: Retrieves transaction history for merchant wallets

- **MerchantAuthViewSet**: Handles merchant-specific authentication
  - `generate_api_key`: Creates new API credentials
  - `revoke_api_key`: Invalidates existing API credentials

#### Key Features

- **Merchant Registration Flow**:
  1. User submits merchant registration form
  2. System validates business information
  3. Admin reviews and approves merchant
  4. Merchant receives API credentials
  5. Merchant can create wallets for customers

- **API Authentication**:
  ```python
  def authenticate_api_request(request):
      api_key = request.headers.get('X-API-Key')
      if not api_key:
          return None
          
      try:
          credential = APICredential.objects.get(api_key=api_key, is_active=True)
          if credential.expires_at and credential.expires_at < timezone.now():
              return None
              
          # Update last used information
          credential.last_used_at = timezone.now()
          credential.last_used_ip = request.META.get('REMOTE_ADDR')
          credential.save(update_fields=['last_used_at', 'last_used_ip'])
          
          return credential.merchant.user
      except APICredential.DoesNotExist:
          return None
  ```

## Integration Points

### Security ↔ Wallets
- CustomUser model is referenced by Wallet model
- Authentication is required for all wallet operations
- Security middleware protects wallet endpoints

### Merchants ↔ Wallets
- Merchants create wallet requests
- Wallets are linked to merchants
- Merchants can view wallets they've created

### Security ↔ Merchants
- MerchantUser profile extends CustomUser
- Authentication controls merchant access
- API credentials are linked to merchant accounts

## Development Guidelines

### Working with the Security Module
- Always use the CustomUser model for user management
- Never store passwords in plain text
- Use the provided authentication utilities for token management
- Implement proper permission checks on all views

### Working with the Wallets Module
- Always validate transactions against limits
- Log all wallet operations in the audit log
- Use the wallet creation flow for all new wallets
- Never modify wallet balance directly

### Working with the Merchants Module
- Validate merchant information during registration
- Use API credentials for programmatic access
- Implement rate limiting for merchant API calls
- Always check merchant approval status

## Testing

Each module includes comprehensive tests:

- **Security Tests**: Authentication, password management, and middleware
- **Wallet Tests**: Creation, transactions, and limits
- **Merchant Tests**: Registration, API credentials, and wallet creation

Run tests with:
```bash
python manage.py test security
python manage.py test wallets
python manage.py test phantom_apps.merchants
```
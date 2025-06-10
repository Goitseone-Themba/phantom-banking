from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone
import pyotp
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("kyc_status", "approved")
        extra_fields.setdefault("role", "admin")

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('merchant', 'Merchant'),
        ('customer', 'Customer'),
    ]

    KYC_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
    ]

    # Core Info
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            MinLengthValidator(4),
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username must contain only letters, numbers, and underscores.'
            )
        ]
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    national_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            MinLengthValidator(6),
            RegexValidator(
                regex=r'^[A-Z0-9]+$',
                message='National ID must contain only uppercase letters and numbers.'
            )
        ]
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    date_of_birth = models.DateField()
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Permissions & Status
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='not_started')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Security
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    destination_account = models.CharField(max_length=100, default='DEFAULT_ACC_0001')
    
    # Email Verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, null=True, blank=True)
    email_verification_token_created = models.DateTimeField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='unverified'
    )
    
    # Password Reset
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)

    # 2FA
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)

    # API
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    api_key_expires = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.account_locked_until = None
        self.save()

    def is_account_locked(self):
        return self.account_locked_until and self.account_locked_until > timezone.now()

    def generate_2fa_secret(self):
        self.two_factor_secret = pyotp.random_base32()
        self.save()
        return self.two_factor_secret

    def verify_2fa_token(self, token):
        if not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token)

    def generate_backup_codes(self):
        codes = [str(uuid.uuid4())[:8] for _ in range(10)]
        self.backup_codes = codes
        self.save()
        return codes

    def verify_backup_code(self, code):
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False

    def generate_api_key(self, expires_in_days=30):
        self.api_key = uuid.uuid4()
        self.api_key_expires = timezone.now() + timezone.timedelta(days=expires_in_days)
        self.save()
        return self.api_key


class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    request_data = models.JSONField(null=True, blank=True)
    response_status = models.IntegerField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.action} - {self.timestamp}"


class SecurityEvent(models.Model):
    EVENT_TYPES = [
        ('login_failed', 'Login Failed'),
        ('login_success', 'Login Success'),
        ('password_change', 'Password Change'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('account_locked', 'Account Locked'),
        ('api_key_generated', 'API Key Generated'),
        ('suspicious_activity', 'Suspicious Activity'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    details = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.event_type} - {self.timestamp}"


class MerchantProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='merchant_profile')
    business_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    admin_name = models.CharField(max_length=255)
    admin_email = models.EmailField()
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} ({self.registration_number})"

    class Meta:
        verbose_name = 'Merchant Profile'
        verbose_name_plural = 'Merchant Profiles'


class EmailVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Verification for {self.user.email}"

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at


class PasswordReset(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Password reset for {self.user.email}"

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

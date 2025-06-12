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
        user.set_password(password)  # This automatically hashes the password
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
        
    def make_random_password(self, length=12):
        """
        Generate a secure random password with mixed characters
        """
        import random
        import string
        
        # Ensure we have at least one of each character type
        lowercase = random.choice(string.ascii_lowercase)
        uppercase = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)
        special = random.choice('!@#$%^&*()-_=+')
        
        # Fill the rest with random characters
        remaining_length = length - 4
        all_chars = string.ascii_letters + string.digits + '!@#$%^&*()-_=+'
        remaining_chars = ''.join(random.choice(all_chars) for _ in range(remaining_length))
        
        # Combine all parts and shuffle
        password_chars = list(lowercase + uppercase + digit + special + remaining_chars)
        random.shuffle(password_chars)
        
        return ''.join(password_chars)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Base user model with common fields for all user types"""
    
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

    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            MinLengthValidator(4),
            RegexValidator(regex=r'^[a-zA-Z0-9_]+$')
        ]
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='not_started')
    
    # Security fields
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Common profile fields
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def is_account_locked(self):
        return self.account_locked_until and self.account_locked_until > timezone.now()

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()


class AdminUser(models.Model):
    """Admin user profile with admin-specific fields"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    access_level = models.CharField(max_length=50, default='standard')
    
    def __str__(self):
        return f"Admin: {self.user.username}"


class MerchantUser(models.Model):
    """Merchant user profile with business-specific fields"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='merchant_profile')
    business_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    business_type = models.CharField(max_length=100)
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
    address = models.TextField()
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Merchant: {self.business_name}"


class CustomerUser(models.Model):
    """Customer user profile with personal information"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    national_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_customers'
    )
    
    def __str__(self):
        return f"Customer: {self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class SecuritySettings(models.Model):
    """Security settings for users"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='security_settings')
    
    # 2FA
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # API access
    api_key = models.UUIDField(default=uuid.uuid4, editable=False)
    api_key_expires = models.DateTimeField(null=True, blank=True)
    
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


class EmailVerification(models.Model):
    """Email verification tokens"""
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
    """Password reset tokens"""
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


class AuditLog(models.Model):
    """System-wide audit log"""
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
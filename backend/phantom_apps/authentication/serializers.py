from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from allauth.account.models import EmailAddress
from dj_rest_auth.serializers import (
    LoginSerializer as DefaultLoginSerializer,
    UserDetailsSerializer as DefaultUserDetailsSerializer,
    PasswordResetSerializer as DefaultPasswordResetSerializer,
    PasswordResetConfirmSerializer as DefaultPasswordResetConfirmSerializer,
)
from .models import User, EmailVerificationToken, LoginAttempt
from .utils import get_client_ip, generate_verification_token


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer with email verification"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    terms_accepted = serializers.BooleanField(write_only=True)
    privacy_accepted = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'phone_number',
            'user_type', 'business_name', 'business_registration',
            'password', 'password_confirm', 'terms_accepted', 'privacy_accepted'
        ]
        extra_kwargs = {
            'username': {'required': False},  # We'll generate it if not provided
            'business_name': {'required': False},
            'business_registration': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username uniqueness if provided"""
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation and terms acceptance"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password confirmation doesn't match.")
        
        if not attrs.get('terms_accepted'):
            raise serializers.ValidationError("You must accept the terms and conditions.")
        
        if not attrs.get('privacy_accepted'):
            raise serializers.ValidationError("You must accept the privacy policy.")
        
        # Business fields validation for merchants
        if attrs.get('user_type') == 'merchant':
            if not attrs.get('business_name'):
                raise serializers.ValidationError("Business name is required for merchant accounts.")
        
        return attrs
    
    def create(self, validated_data):
        """Create user and send verification email"""
        # Remove confirmation fields
        validated_data.pop('password_confirm')
        terms_accepted = validated_data.pop('terms_accepted')
        privacy_accepted = validated_data.pop('privacy_accepted')
        
        # Generate username if not provided
        if not validated_data.get('username'):
            email_prefix = validated_data['email'].split('@')[0]
            base_username = email_prefix[:20]  # Limit length
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            validated_data['username'] = username
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Set acceptance timestamps
        now = timezone.now()
        if terms_accepted:
            user.terms_accepted_at = now
        if privacy_accepted:
            user.privacy_accepted_at = now
        user.save()
        
        # Create email verification token
        from .tasks import send_verification_email
        send_verification_email.delay(user.id)
        
        return user


class LoginSerializer(DefaultLoginSerializer):
    """Custom login serializer with additional security features"""
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Track login attempt
            request = self.context.get('request')
            ip_address = get_client_ip(request) if request else None
            user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
            
            # Try to find user by email or username
            try:
                if '@' in username:
                    user_obj = User.objects.get(email=username.lower())
                else:
                    user_obj = User.objects.get(username=username)
            except User.DoesNotExist:
                user_obj = None
            
            # Check if account is locked
            if user_obj and user_obj.is_account_locked:
                LoginAttempt.objects.create(
                    user=user_obj,
                    email_attempted=username if '@' in username else user_obj.email,
                    ip_address=ip_address or '127.0.0.1',
                    user_agent=user_agent,
                    success=False,
                    failure_reason='Account locked'
                )
                raise serializers.ValidationError("Account is temporarily locked. Please try again later.")
            
            # Authenticate user
            user = authenticate(
                request=request,
                username=username,
                password=password
            )
            
            # Record login attempt
            if user_obj:
                LoginAttempt.objects.create(
                    user=user_obj,
                    email_attempted=username if '@' in username else user_obj.email,
                    ip_address=ip_address or '127.0.0.1',
                    user_agent=user_agent,
                    success=bool(user),
                    failure_reason='' if user else 'Invalid credentials'
                )
            else:
                LoginAttempt.objects.create(
                    email_attempted=username,
                    ip_address=ip_address or '127.0.0.1',
                    user_agent=user_agent,
                    success=False,
                    failure_reason='User not found'
                )
            
            if not user:
                if user_obj:
                    user_obj.increment_failed_login()
                raise serializers.ValidationError("Unable to log in with provided credentials.")
            
            # Check if email is verified (optional, can be disabled for development)
            if hasattr(user, 'is_email_verified') and not user.is_email_verified:
                # For now, we'll allow login without email verification
                # but you can uncomment the next lines to enforce it
                # raise serializers.ValidationError(
                #     "Please verify your email address before logging in."
                # )
                pass
            
            # Reset failed login attempts on successful login
            if user_obj:
                user_obj.reset_failed_login()
                # Update last login IP
                user_obj.last_login_ip = ip_address
                user_obj.save(update_fields=['last_login_ip'])
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include username and password.")


class UserDetailsSerializer(DefaultUserDetailsSerializer):
    """Extended user details serializer"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'user_type', 'business_name', 'business_registration',
            'is_email_verified', 'is_phone_verified', 'is_business_verified',
            'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'email', 'user_type', 'is_email_verified',
            'is_phone_verified', 'is_business_verified',
            'date_joined', 'last_login'
        ]


class EmailVerificationSerializer(serializers.Serializer):
    """Email verification serializer"""
    
    token = serializers.CharField(max_length=255)
    
    def validate_token(self, value):
        """Validate verification token"""
        try:
            verification_token = EmailVerificationToken.objects.get(token=value)
            if not verification_token.is_valid:
                if verification_token.is_expired:
                    raise serializers.ValidationError("Verification token has expired.")
                elif verification_token.is_used:
                    raise serializers.ValidationError("Verification token has already been used.")
                else:
                    raise serializers.ValidationError("Invalid verification token.")
            return verification_token
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")
    
    def save(self):
        """Verify email and mark token as used"""
        token = self.validated_data['token']
        
        # Mark user email as verified
        user = token.user
        user.is_email_verified = True
        user.email_verified_at = timezone.now()
        user.save(update_fields=['is_email_verified', 'email_verified_at'])
        
        # Mark token as used
        token.mark_as_used()
        
        return user


class ResendVerificationSerializer(serializers.Serializer):
    """Resend email verification serializer"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email exists and is not already verified"""
        try:
            user = User.objects.get(email=value.lower())
            if user.is_email_verified:
                raise serializers.ValidationError("Email is already verified.")
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email address.")
    
    def save(self):
        """Send new verification email"""
        user = self.validated_data['email']
        from .tasks import send_verification_email
        send_verification_email.delay(user.id)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Change password serializer"""
    
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate_old_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password confirmation doesn't match.")
        return attrs
    
    def save(self):
        """Change user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetSerializer(DefaultPasswordResetSerializer):
    """Custom password reset serializer"""
    
    def validate_email(self, value):
        """Validate email exists"""
        email = value.lower()
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            pass
        return email
    
    def save(self):
        """Send password reset email"""
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email)
            from .tasks import send_password_reset_email
            send_password_reset_email.delay(user.id)
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            pass


class PasswordResetConfirmSerializer(DefaultPasswordResetConfirmSerializer):
    """Custom password reset confirmation serializer"""
    
    def validate(self, attrs):
        """Validate reset token and passwords"""
        # Call parent validation
        attrs = super().validate(attrs)
        
        # Additional validation can be added here
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError("Password confirmation doesn't match.")
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile update serializer"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number',
            'business_name', 'business_registration'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value:
            # Basic phone number validation
            import re
            if not re.match(r'^\+?[1-9]\d{1,14}$', value.replace(' ', '').replace('-', '')):
                raise serializers.ValidationError("Invalid phone number format.")
        return value


class LoginAttemptSerializer(serializers.ModelSerializer):
    """Login attempt serializer for security monitoring"""
    
    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'email_attempted', 'ip_address', 'user_agent',
            'success', 'failure_reason', 'attempted_at', 'country', 'city'
        ]
        read_only_fields = ['id', 'attempted_at']


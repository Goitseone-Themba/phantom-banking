from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import MerchantProfile, EmailVerification, PasswordReset

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'role', 'email_verified', 'verification_status')
        read_only_fields = ('email_verified', 'verification_status')

class MerchantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantProfile
        fields = ('id', 'business_name', 'registration_number', 'contact_email',
                 'contact_phone', 'admin_name', 'admin_email', 'is_approved',
                 'approval_date', 'created_at', 'updated_at')
        read_only_fields = ('is_approved', 'approval_date', 'created_at', 'updated_at')

class MerchantSignupSerializer(serializers.Serializer):
    business_name = serializers.CharField(max_length=255)
    registration_number = serializers.CharField(max_length=100)
    contact_email = serializers.EmailField()
    contact_phone = serializers.CharField(max_length=20)
    admin_name = serializers.CharField(max_length=255)
    admin_email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match")
        
        # Check if registration number is unique
        if MerchantProfile.objects.filter(registration_number=data['registration_number']).exists():
            raise ValidationError("A merchant with this registration number already exists")
        
        # Check if admin email is unique
        if User.objects.filter(email=data['admin_email']).exists():
            raise ValidationError("A user with this email already exists")
        
        return data

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match")
        return data

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()

class CreateWalletSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    initial_balance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise ValidationError("A user with this phone number already exists")
        return value
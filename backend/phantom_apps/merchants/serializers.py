from rest_framework import serializers
from .models import Merchant, APICredential
from django.contrib.auth import get_user_model

User = get_user_model()

class APICredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = APICredential
        fields = [
            'credential_id', 'api_key', 'permissions', 'created_at',
            'expires_at', 'is_active', 'last_used_at', 'last_used_ip'
        ]
        read_only_fields = ['credential_id', 'created_at', 'last_used_at', 'last_used_ip']

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = [
            'merchant_id', 'business_name', 'fnb_account_number',
            'contact_email', 'phone_number', 'registration_number',
            'admin_name', 'admin_email', 'is_approved', 'created_at'
        ]
        read_only_fields = ['merchant_id', 'created_at', 'is_approved']

class MerchantRegistrationSerializer(serializers.Serializer):
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
            raise serializers.ValidationError("Passwords do not match")
        
        # Check if registration number is unique
        if Merchant.objects.filter(registration_number=data['registration_number']).exists():
            raise serializers.ValidationError("A merchant with this registration number already exists")
        
        # Check if admin email is unique
        if User.objects.filter(email=data['admin_email']).exists():
            raise serializers.ValidationError("A user with this email already exists")
        
        return data
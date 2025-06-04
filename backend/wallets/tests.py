from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Merchant, APICredential

class MerchantRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for merchant registration"""
    
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Merchant
        fields = [
            'username', 'password', 'password_confirm',
            'business_name', 'fnb_account_number', 
            'contact_email', 'phone_number', 'business_registration',
            'webhook_url'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        # Extract user data
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=validated_data['contact_email'],
            password=password
        )
        
        # Create merchant
        merchant = Merchant.objects.create(user=user, **validated_data)
        return merchant

class MerchantSerializer(serializers.ModelSerializer):
    """Serializer for merchant data"""
    
    class Meta:
        model = Merchant
        fields = [
            'merchant_id', 'business_name', 'fnb_account_number',
            'contact_email', 'phone_number', 'business_registration',
            'created_at', 'is_active', 'commission_rate', 'webhook_url'
        ]
        read_only_fields = ['merchant_id', 'created_at']

class APICredentialSerializer(serializers.ModelSerializer):
    """Serializer for API credentials"""
    
    class Meta:
        model = APICredential
        fields = [
            'credential_id', 'api_key', 'permissions',
            'created_at', 'expires_at', 'is_active', 'last_used_at'
        ]
        read_only_fields = ['credential_id', 'api_key', 'created_at', 'last_used_at']
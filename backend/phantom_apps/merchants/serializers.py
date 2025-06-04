from rest_framework import serializers
from .models import Merchant, APICredential

class APICredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = APICredential
        fields = [
            'credential_id', 'api_key', 'permissions', 'created_at',
            'expires_at', 'is_active', 'last_used_at', 'last_used_ip'
        ]
        read_only_fields = ['credential_id', 'created_at', 'last_used_at', 'last_used_ip']

class MerchantSerializer(serializers.ModelSerializer):
    credentials = APICredentialSerializer(many=True, read_only=True)
    
    class Meta:
        model = Merchant
        fields = [
            'merchant_id', 'business_name', 'fnb_account_number',
            'contact_email', 'phone_number', 'business_registration',
            'api_key', 'created_at', 'updated_at', 'is_active',
            'commission_rate', 'webhook_url', 'credentials'
        ]
        read_only_fields = ['merchant_id', 'api_key', 'created_at', 'updated_at']
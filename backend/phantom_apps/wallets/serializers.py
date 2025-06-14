"""
Wallet serializers with customer info included
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Wallet
from ..customers.models import Customer
from ..customers.serializers import CustomerSerializer

class WalletCreateResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for wallet creation response including customer info
    """
    customer = CustomerSerializer(read_only=True)
    merchant_id = serializers.UUIDField(source='merchant.merchant_id', read_only=True)
    merchant_business_name = serializers.CharField(source='merchant.business_name', read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'wallet_id',
            'customer',
            'merchant_id', 
            'merchant_business_name',
            'balance',
            'currency',
            'daily_limit',
            'monthly_limit',
            'status',
            'is_frozen',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'wallet_id', 'customer', 'merchant_id', 'merchant_business_name',
            'balance', 'currency', 'daily_limit', 'monthly_limit', 'status',
            'is_frozen', 'created_at', 'updated_at'
        ]

class WalletDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for wallet details including customer info
    Used for retrieving detailed wallet information
    """
    customer = CustomerSerializer(read_only=True)
    merchant_id = serializers.UUIDField(source='merchant.merchant_id', read_only=True)
    merchant_business_name = serializers.CharField(source='merchant.business_name', read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'wallet_id',
            'customer',
            'merchant_id', 
            'merchant_business_name',
            'balance',
            'currency',
            'daily_limit',
            'monthly_limit',
            'status',
            'is_frozen',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'wallet_id', 'customer', 'merchant_id', 'merchant_business_name',
            'balance', 'currency', 'daily_limit', 'monthly_limit', 'status',
            'is_frozen', 'created_at', 'updated_at'
        ]

class WalletListSerializer(serializers.ModelSerializer):
    """
    Compact wallet serializer for list views (merchant's wallets)
    """
    customer = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='customer.first_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'wallet_id',
            'customer',
            'customer_name',
            'customer_phone', 
            'balance',
            'currency',
            'status',
            'is_frozen',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'wallet_id', 'customer', 'customer_name', 'customer_phone',
            'balance', 'currency', 'status', 'is_frozen', 'created_at', 'updated_at'
        ]
    
    def get_customer(self, obj):
        """Return compact customer info for list view"""
        return {
            'customer_id': obj.customer.customer_id,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name,
            'phone_number': obj.customer.phone_number,
            'email': obj.customer.email
        }


class WalletCreateRequestSerializer(serializers.Serializer):
    """
    Serializer for wallet creation request validation
    """
    # No fields needed - customer_id comes from URL
    pass

    def validate(self, attrs):
        """Custom validation for wallet creation"""
        return attrs


class WalletSummarySerializer(serializers.ModelSerializer):
    """
    Simplified wallet serializer for inclusion in other serializers
    """
    customer_id = serializers.UUIDField(source='customer.customer_id', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'wallet_id',
            'customer_id',
            'customer_name',
            'customer_phone',
            'balance',
            'currency',
            'status',
            'is_frozen'
        ]
        read_only_fields = fields

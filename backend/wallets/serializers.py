from rest_framework import serializers
from .models import Wallet, WalletCreationRequest

class WalletSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    merchant_name = serializers.CharField(source='merchant.business_name', read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'wallet_id', 'username', 'merchant_name', 'balance', 
            'status', 'wallet_type', 'created_at', 'last_transaction',
            'daily_transaction_limit', 'monthly_transaction_limit'
        ]
        read_only_fields = ['wallet_id', 'balance', 'created_at', 'last_transaction']

class WalletCreationRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    
    class Meta:
        model = WalletCreationRequest
        fields = [
            'request_id', 'merchant', 'status', 'first_name', 
            'last_name', 'email', 'phone_number', 'national_id', 
            'date_of_birth', 'username', 'created_at', 'processed_at'
        ]
        read_only_fields = ['request_id', 'status', 'created_at', 'processed_at']
    
    def validate(self, data):
        """
        Custom validation for wallet creation request
        """
        # Validate username if provided
        if 'username' in data:
            username = data['username']
            from security.models import CustomUser
            if CustomUser.objects.filter(username=username).exists():
                raise serializers.ValidationError({"username": "This username is already taken."})
        
        # Validate national ID
        if 'national_id' in data:
            national_id = data['national_id']
            from security.models import CustomerUser
            if CustomerUser.objects.filter(national_id=national_id).exists():
                raise serializers.ValidationError({"national_id": "A customer with this national ID already exists."})
        
        # Validate email
        if 'email' in data:
            email = data['email']
            from security.models import CustomUser
            if CustomUser.objects.filter(email=email).exists():
                raise serializers.ValidationError({"email": "This email is already registered."})
        
        return data
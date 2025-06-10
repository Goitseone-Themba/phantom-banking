from rest_framework import serializers
from .models import Wallet, WalletCreationRequest
from django.core.validators import RegexValidator

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('wallet_id', 'balance', 'created_at', 'updated_at')

class WalletCreationRequestSerializer(serializers.ModelSerializer):
    national_id = serializers.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]+$',
                message='National ID must contain only uppercase letters and numbers.'
            )
        ]
    )
    
    class Meta:
        model = WalletCreationRequest
        fields = (
            'request_id', 'merchant', 'first_name', 'last_name', 
            'email', 'phone_number', 'national_id', 'date_of_birth',
            'status', 'created_at', 'processed_at'
        )
        read_only_fields = ('request_id', 'status', 'created_at', 'processed_at')
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must start with '+' followed by country code."
            )
        return value
    
    def validate(self, data):
        """Additional validation"""
        # Check if a pending request already exists for this National ID
        if WalletCreationRequest.objects.filter(
            national_id=data['national_id'],
            status='pending'
        ).exists():
            raise serializers.ValidationError(
                "A pending wallet request already exists for this National ID."
            )
        return data
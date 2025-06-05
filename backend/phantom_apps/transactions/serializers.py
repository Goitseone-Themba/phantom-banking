from decimal import Decimal
from rest_framework import serializers
from .models import QRCode, EFTPayment, Transaction
from ..merchants.models import Merchant
from ..customers.models import Customer
from ..wallets.models import Wallet


class QRCodeCreateSerializer(serializers.Serializer):
    """Serializer for creating QR codes"""
    merchant_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    expires_in_minutes = serializers.IntegerField(min_value=1, max_value=1440, default=15)
    
    def validate_merchant_id(self, value):
        """Validate merchant exists"""
        try:
            Merchant.objects.get(id=value)
            return value
        except Merchant.DoesNotExist:
            raise serializers.ValidationError("Merchant not found")


class QRCodeSerializer(serializers.ModelSerializer):
    """Serializer for QR code responses"""
    merchant_name = serializers.CharField(source='merchant.business_name', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = QRCode
        fields = [
            'id', 'qr_token', 'amount', 'description', 'reference',
            'merchant_name', 'status', 'expires_at', 'created_at',
            'is_valid', 'is_expired', 'qr_data'
        ]
        read_only_fields = ['id', 'qr_token', 'created_at']


class QRCodePaymentSerializer(serializers.Serializer):
    """Serializer for processing QR code payments"""
    customer_phone = serializers.CharField(max_length=15)
    wallet_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_customer_phone(self, value):
        """Validate customer exists"""
        try:
            Customer.objects.get(phone_number=value)
            return value
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer not found")
    
    def validate_wallet_id(self, value):
        """Validate wallet exists if provided"""
        if value:
            try:
                Wallet.objects.get(id=value)
                return value
            except Wallet.DoesNotExist:
                raise serializers.ValidationError("Wallet not found")
        return value


class EFTPaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating EFT payments"""
    customer_phone = serializers.CharField(max_length=15)
    wallet_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('10.00'))
    bank_code = serializers.ChoiceField(choices=[
        ('fnb', 'First National Bank'),
        ('standard', 'Standard Bank'),
        ('barclays', 'Barclays Bank'),
        ('nedbank', 'Nedbank'),
        ('choppies', 'Choppies Bank'),
    ])
    account_number = serializers.CharField(max_length=50)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_customer_phone(self, value):
        """Validate customer exists"""
        try:
            Customer.objects.get(phone_number=value)
            return value
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer not found")
    
    def validate_wallet_id(self, value):
        """Validate wallet exists"""
        try:
            Wallet.objects.get(id=value)
            return value
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Wallet not found")
    
    def validate(self, attrs):
        """Validate customer owns the wallet"""
        customer_phone = attrs.get('customer_phone')
        wallet_id = attrs.get('wallet_id')
        
        if customer_phone and wallet_id:
            try:
                customer = Customer.objects.get(phone_number=customer_phone)
                wallet = Wallet.objects.get(id=wallet_id)
                if wallet.customer != customer:
                    raise serializers.ValidationError("Wallet does not belong to customer")
            except (Customer.DoesNotExist, Wallet.DoesNotExist):
                pass  # Will be caught by individual field validators
        
        return attrs


class EFTPaymentSerializer(serializers.ModelSerializer):
    """Serializer for EFT payment responses"""
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    wallet_balance = serializers.DecimalField(source='wallet.balance', max_digits=15, decimal_places=2, read_only=True)
    transaction_id = serializers.UUIDField(source='transaction.id', read_only=True)
    
    class Meta:
        model = EFTPayment
        fields = [
            'id', 'amount', 'bank_code', 'account_number', 'reference',
            'status', 'external_reference', 'created_at', 'processed_at',
            'completed_at', 'customer_phone', 'customer_name', 
            'wallet_balance', 'transaction_id', 'response_data'
        ]
        read_only_fields = [
            'id', 'status', 'external_reference', 'created_at',
            'processed_at', 'completed_at', 'response_data'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction responses"""
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    merchant_name = serializers.CharField(source='merchant.business_name', read_only=True)
    from_wallet_balance = serializers.DecimalField(source='from_wallet.balance', max_digits=15, decimal_places=2, read_only=True)
    to_wallet_balance = serializers.DecimalField(source='to_wallet.balance', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'amount', 'fee', 'net_amount',
            'status', 'reference', 'description', 'created_at',
            'completed_at', 'customer_phone', 'customer_name',
            'merchant_name', 'from_wallet_balance', 'to_wallet_balance',
            'metadata'
        ]
        read_only_fields = [
            'id', 'net_amount', 'created_at', 'completed_at'
        ]


class TransactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for transaction lists"""
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    merchant_name = serializers.CharField(source='merchant.business_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'amount', 'status',
            'created_at', 'customer_phone', 'merchant_name'
        ]


class PaymentSummarySerializer(serializers.Serializer):
    """Serializer for payment summaries"""
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_transactions = serializers.IntegerField()
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    date_range = serializers.CharField()
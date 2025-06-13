from rest_framework import serializers
from decimal import Decimal
import uuid

from .models import Transaction, PaymentMethod, TransactionStatus, QRCode, EFTPayment
from ..wallets.serializers import WalletSummarySerializer
from ..merchants.models import Merchant
from ..customers.models import Customer
from ..wallets.models import Wallet


# Base serializers for lookup models
class TransactionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionStatus
        fields = ['code', 'name']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['code', 'name']


# Base transaction serializers
class TransactionSerializer(serializers.ModelSerializer):
    """Comprehensive transaction serializer"""
    status = TransactionStatusSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    wallet = WalletSummarySerializer(read_only=True)
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    merchant_name = serializers.CharField(source='merchant.business_name', read_only=True)
    from_wallet_balance = serializers.DecimalField(source='from_wallet.balance', max_digits=15, decimal_places=2, read_only=True)
    to_wallet_balance = serializers.DecimalField(source='to_wallet.balance', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_id', 'wallet', 'amount', 'fee', 'net_amount', 'currency',
            'transaction_type', 'status', 'payment_method', 'reference', 'reference_number',
            'description', 'external_reference', 'metadata', 'payment_details',
            'is_reconciled', 'failure_reason', 'created_at', 'updated_at', 'completed_at',
            'customer_phone', 'customer_name', 'merchant_name', 
            'from_wallet_balance', 'to_wallet_balance'
        ]
        read_only_fields = [
            'transaction_id', 'net_amount', 'reference_number', 'created_at', 
            'updated_at', 'completed_at'
        ]


class TransactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for transaction lists"""
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    merchant_name = serializers.CharField(source='merchant.business_name', read_only=True)
    status_code = serializers.CharField(source='status.code', read_only=True)
    payment_method_code = serializers.CharField(source='payment_method.code', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_id', 'transaction_type', 'amount', 'status_code',
            'payment_method_code', 'created_at', 'customer_phone', 'merchant_name'
        ]


class TransactionCreateSerializer(serializers.Serializer):
    """Base serializer for creating transactions"""
    wallet_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value


class TransactionResponseSerializer(serializers.Serializer):
    """Serializer for transaction responses"""
    transaction_id = serializers.UUIDField()
    wallet_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = serializers.CharField()
    status = serializers.CharField()
    payment_method = serializers.CharField()
    reference = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.DateTimeField()


# QR Code serializers
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


class QRPaymentSerializer(TransactionCreateSerializer):
    """Serializer for QR code payments (merchant perspective)"""
    qr_code = serializers.CharField(max_length=255)
    
    def validate_qr_code(self, value):
        """Validate QR code format"""
        if len(value) < 10:
            raise serializers.ValidationError("QR code is too short or invalid")
        return value


# EFT Payment serializers
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
    transaction_id = serializers.UUIDField(source='transaction.transaction_id', read_only=True)
    bank_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EFTPayment
        fields = [
            'id', 'amount', 'bank_code', 'bank_name', 'account_number', 'reference',
            'status', 'external_reference', 'created_at', 'processed_at',
            'completed_at', 'customer_phone', 'customer_name', 
            'wallet_balance', 'transaction_id', 'response_data'
        ]
        read_only_fields = [
            'id', 'status', 'external_reference', 'created_at',
            'processed_at', 'completed_at', 'response_data'
        ]
    
    def get_bank_name(self, obj):
        """Get full bank name from code"""
        bank_mapping = dict(EFTPayment.BANK_CHOICES)
        return bank_mapping.get(obj.bank_code, obj.bank_code)


class EFTPaymentSerializer(TransactionCreateSerializer):
    """Serializer for EFT payments (merchant perspective)"""
    bank_name = serializers.CharField(max_length=100)
    account_number = serializers.CharField(max_length=20)
    
    def validate_account_number(self, value):
        """Validate bank account number format"""
        if not value.isdigit() or len(value) < 8:
            raise serializers.ValidationError("Invalid bank account number format")
        return value


# Summary and analytics serializers
class PaymentSummarySerializer(serializers.Serializer):
    """Serializer for payment summaries"""
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_transactions = serializers.IntegerField()
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    date_range = serializers.CharField()


class TransactionSummarySerializer(serializers.Serializer):
    """Serializer for transaction summary statistics"""
    total_transactions = serializers.IntegerField()
    transaction_counts = serializers.DictField()
    transaction_volumes = serializers.DictField()
    payment_methods = serializers.DictField()
    recent_transactions = serializers.ListField()


# Webhook serializers
class EFTWebhookSerializer(serializers.Serializer):
    """Serializer for EFT webhook data"""
    reference = serializers.CharField(max_length=100)
    status = serializers.CharField(max_length=20)
    fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    timestamp = serializers.DateTimeField(required=False)
    transaction_id = serializers.CharField(max_length=100, required=False)
    error_code = serializers.CharField(max_length=50, required=False)
    error_message = serializers.CharField(max_length=255, required=False)


# Error response serializers
class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response format"""
    error = serializers.BooleanField(default=True)
    error_code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    status_code = serializers.IntegerField()


class SuccessResponseSerializer(serializers.Serializer):
    """Standard success response format"""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    status_code = serializers.IntegerField()
    data = serializers.DictField(required=False)
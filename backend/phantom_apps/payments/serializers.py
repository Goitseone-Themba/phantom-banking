from rest_framework import serializers
from .models import PaymentProvider, Payment, PaymentRefund

class PaymentProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProvider
        fields = ['id', 'name', 'code', 'description', 'is_active', 'config', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'config': {'write_only': True}
        }

class PaymentRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'refund_id', 'payment', 'amount', 'reason', 'status',
            'provider_reference', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'refund_id', 'status', 'provider_reference', 'created_at',
            'updated_at', 'completed_at'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    refunds = PaymentRefundSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'user', 'provider', 'provider_name', 'amount',
            'currency', 'status', 'provider_reference', 'description', 'metadata',
            'created_at', 'updated_at', 'completed_at', 'refunds'
        ]
        read_only_fields = [
            'payment_id', 'status', 'provider_reference', 'created_at',
            'updated_at', 'completed_at', 'refunds'
        ]

    def create(self, validated_data):
        # Generate a unique payment ID
        import uuid
        validated_data['payment_id'] = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        return super().create(validated_data)
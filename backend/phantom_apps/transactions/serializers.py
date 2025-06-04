from rest_framework import serializers
from .models import Transaction, TransactionFee

class TransactionFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionFee
        fields = ['amount', 'description', 'created_at']
        read_only_fields = ['created_at']

class TransactionSerializer(serializers.ModelSerializer):
    fee = TransactionFeeSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'transaction_type', 'amount', 'currency',
            'status', 'source_account', 'destination_account', 'description',
            'reference', 'created_at', 'updated_at', 'completed_at', 'fee'
        ]
        read_only_fields = [
            'transaction_id', 'status', 'created_at', 'updated_at', 
            'completed_at', 'fee'
        ]

    def create(self, validated_data):
        # Generate a unique transaction ID
        import uuid
        validated_data['transaction_id'] = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        return super().create(validated_data)
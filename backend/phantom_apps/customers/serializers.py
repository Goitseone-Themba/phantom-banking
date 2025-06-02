from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer data"""
    
    class Meta:
        model = Customer
        fields = [
            'customer_id', 'first_name', 'last_name', 
            'phone_number', 'email', 'identity_number',
            'created_at', 'status', 'is_verified',
            'preferred_language', 'nationality'
        ]
        read_only_fields = ['customer_id', 'created_at']

class CustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating customers"""
    
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'phone_number', 
            'email', 'identity_number', 'preferred_language', 'nationality'
        ]
    
    def create(self, validated_data):
        # Get merchant from request context
        merchant = self.context['request'].user.merchant
        return Customer.objects.create(merchant=merchant, **validated_data)

from rest_framework import serializers
from .models import KYCVerification, FNBAccountConversion

class KYCVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        fields = [
            'id', 'user', 'document_type', 'document_file',
            'status', 'verification_notes', 'submitted_at', 'verified_at'
        ]
        read_only_fields = ['status', 'verification_notes', 'verified_at']

    def validate_document_file(self, value):
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError('File size cannot exceed 10MB')
        return value

class FNBAccountConversionSerializer(serializers.ModelSerializer):
    kyc_verification = KYCVerificationSerializer(read_only=True)
    kyc_verification_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FNBAccountConversion
        fields = [
            'id', 'user', 'wallet_id', 'kyc_verification',
            'kyc_verification_id', 'status', 'requested_at',
            'processed_at', 'rejection_reason', 'fnb_account_number'
        ]
        read_only_fields = [
            'status', 'processed_at', 'rejection_reason',
            'fnb_account_number'
        ]

    def validate_kyc_verification_id(self, value):
        try:
            kyc = KYCVerification.objects.get(id=value)
            if kyc.status != 'verified':
                raise serializers.ValidationError(
                    'KYC verification must be completed before converting to FNB account'
                )
            return value
        except KYCVerification.DoesNotExist:
            raise serializers.ValidationError('Invalid KYC verification ID')
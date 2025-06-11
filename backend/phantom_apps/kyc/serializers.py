from rest_framework import serializers
from django.contrib.auth.models import User
from .models import KYCRecord, KYCDocument, KYCEvent

class KYCRecordSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = KYCRecord
        fields = [
            'id', 'user_email', 'status', 'verification_level',
            'first_name', 'last_name', 'date_of_birth', 'nationality',
            'document_type', 'document_number', 'address_line_1', 'address_line_2',
            'city', 'state_province', 'postal_code', 'country',
            'risk_score', 'risk_level', 'created_at', 'updated_at',
            'verified_at', 'expires_at', 'is_verified', 'is_expired',
            'veriff_session_url', 'admin_notes'
        ]
        read_only_fields = [
            'id', 'user_email', 'status', 'risk_score', 'risk_level',
            'created_at', 'updated_at', 'verified_at', 'expires_at',
            'is_verified', 'is_expired', 'veriff_session_url', 'admin_notes'
        ]

    def validate_date_of_birth(self, value):
        from django.utils import timezone
        from datetime import timedelta
        
        # Must be at least 18 years old
        min_age_date = timezone.now().date() - timedelta(days=18*365)
        if value > min_age_date:
            raise serializers.ValidationError("Must be at least 18 years old")
        return value

    def validate_document_number(self, value):
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Document number must be at least 5 characters")
        return value.strip()


class KYCStartVerificationSerializer(serializers.Serializer):
    """Serializer for starting KYC verification process"""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField()
    nationality = serializers.CharField(max_length=3)
    document_type = serializers.ChoiceField(choices=['passport', 'id_card', 'driving_license'])
    document_number = serializers.CharField(max_length=100)
    address_line_1 = serializers.CharField(max_length=200)
    address_line_2 = serializers.CharField(max_length=200, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100)
    state_province = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=3)

    def validate_date_of_birth(self, value):
        from django.utils import timezone
        from datetime import timedelta
        
        min_age_date = timezone.now().date() - timedelta(days=18*365)
        if value > min_age_date:
            raise serializers.ValidationError("Must be at least 18 years old")
        return value


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ['id', 'document_type', 'file_url', 'file_name', 'uploaded_at', 'verified']
        read_only_fields = ['id', 'uploaded_at', 'verified']


class KYCEventSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = KYCEvent
        fields = ['id', 'event_type', 'description', 'metadata', 'created_at', 'created_by_email']
        read_only_fields = ['id', 'created_at', 'created_by_email']

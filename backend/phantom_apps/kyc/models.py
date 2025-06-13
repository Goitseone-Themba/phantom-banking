# backend/phantom_apps/kyc/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class KYCRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        RESUBMISSION_REQUESTED = 'resubmission_requested', 'Resubmission Requested'

    class VerificationLevel(models.TextChoices):
        BASIC = 'basic', 'Basic'
        ENHANCED = 'enhanced', 'Enhanced'
        PREMIUM = 'premium', 'Premium'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc_record')
    
    # Veriff Integration Fields
    veriff_session_id = models.CharField(max_length=255, null=True, blank=True)
    veriff_session_url = models.URLField(null=True, blank=True)
    veriff_decision = models.CharField(max_length=50, null=True, blank=True)
    veriff_code = models.CharField(max_length=10, null=True, blank=True)
    veriff_reason = models.TextField(null=True, blank=True)
    
    # KYC Status
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    verification_level = models.CharField(max_length=20, choices=VerificationLevel.choices, default=VerificationLevel.BASIC)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=3)  # ISO country code
    document_type = models.CharField(max_length=50)  # passport, id_card, driving_license
    document_number = models.CharField(max_length=100)
    
    # Address Information
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=3)  # ISO country code
    
    # Verification Data
    document_front_image = models.URLField(null=True, blank=True)
    document_back_image = models.URLField(null=True, blank=True)
    selfie_image = models.URLField(null=True, blank=True)
    
    # Risk Assessment
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    risk_level = models.CharField(max_length=20, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Admin fields
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_kyc_records')
    admin_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'kyc_records'
        ordering = ['-created_at']

    def __str__(self):
        return f"KYC Record for {self.user.username} - {self.status}"

    @property
    def is_verified(self):
        return self.status == self.Status.APPROVED

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def approve(self, reviewed_by=None):
        self.status = self.Status.APPROVED
        self.verified_at = timezone.now()
        self.expires_at = timezone.now() + timezone.timedelta(days=365)  # Valid for 1 year
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.save()

    def reject(self, reason=None, reviewed_by=None):
        self.status = self.Status.REJECTED
        if reason:
            self.admin_notes = reason
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.save()


class KYCDocument(models.Model):
    class DocumentType(models.TextChoices):
        PASSPORT = 'passport', 'Passport'
        ID_CARD = 'id_card', 'ID Card'
        DRIVING_LICENSE = 'driving_license', 'Driving License'
        PROOF_OF_ADDRESS = 'proof_of_address', 'Proof of Address'
        BANK_STATEMENT = 'bank_statement', 'Bank Statement'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kyc_record = models.ForeignKey(KYCRecord, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    file_url = models.URLField()
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'kyc_documents'

    def __str__(self):
        return f"{self.document_type} for {self.kyc_record.user.username}"


class KYCEvent(models.Model):
    """Track KYC status changes and events"""
    class EventType(models.TextChoices):
        SESSION_CREATED = 'session_created', 'Session Created'
        DOCUMENTS_UPLOADED = 'documents_uploaded', 'Documents Uploaded'
        VERIFICATION_STARTED = 'verification_started', 'Verification Started'
        VERIFICATION_COMPLETED = 'verification_completed', 'Verification Completed'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        EXPIRED = 'expired', 'Expired'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kyc_record = models.ForeignKey(KYCRecord, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'kyc_events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.kyc_record.user.username}"
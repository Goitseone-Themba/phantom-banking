from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class KYCVerification(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    )

    DOCUMENT_TYPE_CHOICES = (
        ('id_document', 'ID Document'),
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
        ('proof_of_address', 'Proof of Address'),
        ('bank_statement', 'Bank Statement')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kyc_verifications')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    document_file = models.FileField(
        upload_to='kyc_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']

class FNBAccountConversion(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fnb_conversions')
    wallet_id = models.CharField(max_length=100)
    kyc_verification = models.ForeignKey(KYCVerification, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    fnb_account_number = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
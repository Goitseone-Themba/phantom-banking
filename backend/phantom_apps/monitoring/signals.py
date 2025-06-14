import time
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.utils import timezone

from .metrics import (
    customers_total, customers_verified, merchants_total, merchants_active,
    wallets_total, wallets_frozen, wallets_kyc_verified, transactions_total,
    transactions_amount, qr_codes_generated, kyc_verifications_total,
    eft_payments_total, security_failed_logins, app_active_sessions
)


@receiver(post_save, sender='customers.Customer')
def customer_created(sender, instance, created, **kwargs):
    """Track customer creation and verification"""
    if created:
        # New customer created - metrics will be updated by collect_business_metrics
        pass
    elif instance.is_verified:
        # Customer verified
        pass


@receiver(post_save, sender='merchants.Merchant')
def merchant_created(sender, instance, created, **kwargs):
    """Track merchant creation and status changes"""
    if created:
        # New merchant created
        pass
    elif hasattr(instance, '_state') and instance._state.adding is False:
        # Merchant updated
        pass


@receiver(post_save, sender='wallets.Wallet')
def wallet_created(sender, instance, created, **kwargs):
    """Track wallet creation and status changes"""
    if created:
        # New wallet created
        pass


@receiver(post_save, sender='transactions.Transaction')
def transaction_created(sender, instance, created, **kwargs):
    """Track transaction events"""
    if created:
        # Track transaction creation
        transactions_total.labels(
            type=instance.transaction_type,
            status=str(instance.status)
        ).inc()
        
        # Track transaction amount
        transactions_amount.labels(
            type=instance.transaction_type
        ).observe(float(instance.amount))


@receiver(post_save, sender='transactions.QRCode')
def qr_code_generated(sender, instance, created, **kwargs):
    """Track QR code generation"""
    if created:
        qr_codes_generated.inc()


@receiver(post_save, sender='kyc.KYCRecord')
def kyc_verification_updated(sender, instance, created, **kwargs):
    """Track KYC verification events"""
    if not created and hasattr(instance, '_state'):
        # KYC status updated
        kyc_verifications_total.labels(status=str(instance.status)).inc()


@receiver(post_save, sender='transactions.EFTPayment')
def eft_payment_created(sender, instance, created, **kwargs):
    """Track EFT payment events"""
    if created:
        eft_payments_total.labels(
            bank=instance.bank_code,
            status=str(instance.status)
        ).inc()


@receiver(user_login_failed)
def track_failed_login(sender, credentials, request, **kwargs):
    """Track failed login attempts for security monitoring"""
    ip_address = get_client_ip(request)
    security_failed_logins.labels(ip_address=ip_address).inc()


@receiver(user_logged_in)
def track_successful_login(sender, user, request, **kwargs):
    """Track successful logins for session monitoring"""
    # Sessions are tracked via Django sessions framework
    pass


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or 'unknown'


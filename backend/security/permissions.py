from rest_framework import permissions
from django.utils import timezone

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'merchant'

class IsVerifiedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.kyc_status == 'verified' and
            not request.user.is_account_locked()
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow admin to access any object
        if request.user.role == 'admin':
            return True
        # Check if the object has a user field and if it matches the request user
        return hasattr(obj, 'user') and obj.user == request.user

class IsMerchantOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['merchant', 'admin']
        )

class CanManageWallet(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin can manage any wallet
        if request.user.role == 'admin':
            return True
        
        # Merchant can manage wallets linked to their business
        if request.user.role == 'merchant':
            return obj.merchant == request.user
            
        # Users can only view their own wallets
        return obj.user == request.user and request.method in permissions.SAFE_METHODS

class CanVerifyKYC(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        # Only admins can verify KYC documents
        return request.user.role == 'admin'

class CanSubmitKYC(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Check if user has already submitted KYC that is pending or verified
        kyc_status = request.user.kyc_status
        return kyc_status in ['not_started', 'rejected']

class CanManageCustomers(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['merchant', 'admin']
        )

    def has_object_permission(self, request, view, obj):
        # Admin can manage any customer
        if request.user.role == 'admin':
            return True
            
        # Merchants can only manage their own customers
        if request.user.role == 'merchant':
            # Check if the customer has a wallet linked to this merchant
            return obj.wallets.filter(merchant=request.user).exists()
            
        return False

class HasValidAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return False
            
        # TODO: Implement API key validation logic
        return True

class RateLimitPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Check if user is rate limited
        if request.user.is_account_locked():
            return False
            
        # TODO: Implement rate limiting logic
        return True
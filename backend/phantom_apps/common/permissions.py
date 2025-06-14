from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsMerchantOwner(BasePermission):
    """
    Custom permission to only allow merchants to access their own data.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a merchant attribute and if it matches the user
        if hasattr(obj, 'merchant'):
            return obj.merchant.user == request.user
        return False

class IsWalletOwner(BasePermission):
    """
    Custom permission to only allow wallet owners to access their wallets.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a customer or merchant relationship
        if hasattr(obj, 'customer') and hasattr(obj.customer, 'merchant'):
            return obj.customer.merchant.user == request.user
        return False

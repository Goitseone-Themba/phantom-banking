from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'merchant'

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow admin to access any object
        if request.user.role == 'admin':
            return True
        # Check if the object has a user field and if it matches the request user
        return hasattr(obj, 'user') and obj.user == request.user
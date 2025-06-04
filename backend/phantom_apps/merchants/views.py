from rest_framework import viewsets, permissions
from .models import Merchant, APICredential
from .serializers import MerchantSerializer, APICredentialSerializer

class MerchantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing merchant details.
    """
    serializer_class = MerchantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Merchant.objects.all()
        return Merchant.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MerchantAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing merchant account settings and profile.
    """
    serializer_class = MerchantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Merchant.objects.filter(user=self.request.user)

class MerchantTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing merchant transactions.
    This is a placeholder and should be implemented based on your transaction model.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # This should be implemented based on your transaction model
        return []
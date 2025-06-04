from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import KYCVerification, FNBAccountConversion
from .serializers import KYCVerificationSerializer, FNBAccountConversionSerializer

class KYCVerificationViewSet(viewsets.ModelViewSet):
    serializer_class = KYCVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return KYCVerification.objects.all()
        return KYCVerification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def verify(self, request, pk=None):
        kyc = self.get_object()
        status = request.data.get('status')
        notes = request.data.get('verification_notes', '')

        if status not in ['verified', 'rejected']:
            return Response(
                {'error': 'Invalid status. Must be "verified" or "rejected"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        kyc.status = status
        kyc.verification_notes = notes
        kyc.verified_at = timezone.now()
        kyc.save()

        # Update user's KYC status
        user = kyc.user
        user.kyc_status = status
        user.save()

        return Response(self.get_serializer(kyc).data)

class FNBAccountConversionViewSet(viewsets.ModelViewSet):
    serializer_class = FNBAccountConversionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return FNBAccountConversion.objects.all()
        return FNBAccountConversion.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Check if user has completed KYC
        if self.request.user.kyc_status != 'verified':
            raise permissions.PermissionDenied(
                'KYC verification must be completed before converting to FNB account'
            )
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def process(self, request, pk=None):
        conversion = self.get_object()
        status = request.data.get('status')
        
        if status not in ['approved', 'rejected']:
            return Response(
                {'error': 'Invalid status. Must be "approved" or "rejected"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversion.status = status
        conversion.processed_at = timezone.now()

        if status == 'approved':
            # In a real implementation, this would integrate with FNB's API
            # For now, we'll generate a mock account number
            import random
            conversion.fnb_account_number = f'FNB{random.randint(10000000, 99999999)}'
        else:
            conversion.rejection_reason = request.data.get('rejection_reason', '')

        conversion.save()
        return Response(self.get_serializer(conversion).data)
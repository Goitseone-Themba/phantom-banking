from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Wallet, WalletCreationRequest
from .serializers import WalletSerializer, WalletCreationRequestSerializer
from security.models import CustomUser
from merchants.models import Merchant

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'merchant':
            return Wallet.objects.filter(merchant__user=user)
        elif user.role == 'customer':
            return Wallet.objects.filter(customer__user=user)
        return super().get_queryset()

class WalletCreationRequestViewSet(viewsets.ModelViewSet):
    queryset = WalletCreationRequest.objects.all()
    serializer_class = WalletCreationRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'merchant':
            return WalletCreationRequest.objects.filter(merchant__user=user)
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        """Create a new wallet creation request"""
        # Add the merchant to the request data
        merchant = get_object_or_404(Merchant, user=request.user)
        request.data['merchant'] = merchant.id
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet_request = serializer.save()
        
        # Send notification email
        wallet_request.send_notification_email()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a wallet creation request"""
        wallet_request = self.get_object()
        
        if wallet_request.status != 'pending':
            return Response(
                {'error': 'This request has already been processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the customer user account
        customer = CustomUser.objects.create_user(
            username=f"customer_{wallet_request.national_id}",
            email=wallet_request.email,
            password=CustomUser.objects.make_random_password(),
            first_name=wallet_request.first_name,
            last_name=wallet_request.last_name,
            national_id=wallet_request.national_id,
            phone_number=wallet_request.phone_number,
            date_of_birth=wallet_request.date_of_birth,
            role='customer'
        )
        
        # Create the wallet
        wallet = Wallet.objects.create(
            customer=customer,
            merchant=wallet_request.merchant
        )
        
        # Update request status
        wallet_request.status = 'approved'
        wallet_request.processed_at = timezone.now()
        wallet_request.save()
        
        # Send notification email
        wallet_request.send_notification_email()
        
        return Response({
            'message': 'Wallet creation request approved successfully.',
            'wallet_id': wallet.wallet_id
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a wallet creation request"""
        wallet_request = self.get_object()
        
        if wallet_request.status != 'pending':
            return Response(
                {'error': 'This request has already been processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wallet_request.status = 'rejected'
        wallet_request.processed_at = timezone.now()
        wallet_request.save()
        
        # Send notification email
        wallet_request.send_notification_email()
        
        return Response({'message': 'Wallet creation request rejected successfully.'})
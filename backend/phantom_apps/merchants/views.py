from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Merchant, APICredential
from .serializers import MerchantSerializer, APICredentialSerializer, MerchantRegistrationSerializer
from django.contrib.auth import get_user_model
# Import needed for wallet creation
from django.shortcuts import get_object_or_404
from django.utils import timezone

User = get_user_model()

class MerchantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing merchant details.
    """
    serializer_class = MerchantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Merchant.objects.none()
        if self.request.user.is_staff:
            return Merchant.objects.all()
        return Merchant.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        Register a new merchant account
        """
        serializer = MerchantRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                # Create user
                user = User.objects.create_user(
                    username=data['admin_name'],
                    email=data['admin_email'],
                    password=data['password'],
                    role='merchant'
                )
                
                # Create merchant
                merchant = Merchant.objects.create(
                    user=user,
                    business_name=data['business_name'],
                    registration_number=data['registration_number'],
                    contact_email=data['contact_email'],
                    phone_number=data['contact_phone'],
                    admin_name=data['admin_name'],
                    admin_email=data['admin_email']
                )
                
                # Create merchant profile in security app
                from security.models import MerchantProfile
                merchant_profile = MerchantProfile.objects.create(
                    user=user,
                    business_name=data['business_name'],
                    registration_number=data['registration_number'],
                    contact_email=data['contact_email'],
                    contact_phone=data['contact_phone'],
                    admin_name=data['admin_name'],
                    admin_email=data['admin_email']
                )
                
                # Send verification email
                from security.auth_utils import send_verification_email
                send_verification_email(user)
                
                return Response({
                    'message': 'Merchant account created successfully. Please check your email to verify your account.',
                    'user_id': user.id,
                    'merchant_id': merchant.merchant_id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def create_wallet_request(self, request, pk=None):
        """
        Create a wallet request for a customer through the merchant.
        """
        merchant = self.get_object()
        
        # Ensure the requesting user owns this merchant
        if merchant.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to create wallet requests for this merchant'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Create a dictionary with the necessary data instead of using serializer
        from wallets.models import WalletCreationRequest
        
        # Add merchant to request data
        # Create wallet request directly
        wallet_request = WalletCreationRequest(
            merchant=merchant,
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            email=request.data.get('email'),
            phone_number=request.data.get('phone_number'),
            national_id=request.data.get('national_id'),
            date_of_birth=request.data.get('date_of_birth')
        )
        wallet_request.save()
        
        return Response(
            {'message': 'Wallet creation request submitted successfully',
             'request_id': str(wallet_request.request_id)},
            status=status.HTTP_201_CREATED
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MerchantAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing merchant account settings and profile.
    """
    serializer_class = MerchantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Merchant.objects.none()
        return Merchant.objects.filter(user=self.request.user)
        
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Get the merchant profile for the authenticated user.
        """
        try:
            merchant = Merchant.objects.get(user=request.user)
            serializer = self.get_serializer(merchant)
            return Response(serializer.data)
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'Merchant profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class MerchantTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing merchant transactions.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # Import here to avoid circular imports
            from phantom_apps.transactions.models import Transaction
            return Transaction.objects.none()
            
        # Simplified approach to avoid import issues
        if not hasattr(self.request.user, 'merchant'):
            return []
            
        # Import here to avoid circular imports
        from wallets.models import Wallet
        from phantom_apps.transactions.models import Transaction
        
        merchant = self.request.user.merchant
        # Get all wallets associated with this merchant
        wallets = Wallet.objects.filter(merchant=merchant)
        
        # Get all transactions for these wallets
        return Transaction.objects.filter(wallet__in=wallets)
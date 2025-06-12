from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Wallet, WalletCreationRequest
from .serializers import WalletSerializer, WalletCreationRequestSerializer
from security.models import CustomUser
from phantom_apps.merchants.models import Merchant as MerchantModel

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Check if this is a swagger schema generation request
        if getattr(self, 'swagger_fake_view', False):
            return Wallet.objects.none()
            
        if user.role == 'merchant':
            return Wallet.objects.filter(merchant__user=user)
        elif user.role == 'customer':
            return Wallet.objects.filter(user=user)
        return super().get_queryset()

class WalletCreationRequestViewSet(viewsets.ModelViewSet):
    queryset = WalletCreationRequest.objects.all()
    serializer_class = WalletCreationRequestSerializer
    # PRODUCTION CODE: Require authentication
    # permission_classes = [IsAuthenticated]
    # TESTING CODE: No authentication required
    permission_classes = []  # Temporarily removed authentication for testing
    http_method_names = ['post', 'head', 'options']  # Only allow POST requests
    
    def get_queryset(self):
        user = self.request.user
        # Check if this is a swagger schema generation request
        if getattr(self, 'swagger_fake_view', False):
            return WalletCreationRequest.objects.none()
            
        if user.role == 'merchant':
            return WalletCreationRequest.objects.filter(merchant__user=user)
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        """Create a new wallet creation request"""
        # PRODUCTION CODE: Merchant-based wallet creation
        # # Verify the user is a merchant
        # if request.user.is_authenticated and request.user.role == 'merchant':
        #     merchant = get_object_or_404(MerchantModel, user=request.user)
        # else:
        #     return Response(
        #         {'error': 'Only merchants can create wallet requests'},
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        
        # TESTING CODE: Use the first merchant
        from phantom_apps.merchants.models import Merchant
        merchant = Merchant.objects.first()
        if not merchant:
            return Response(
                {'error': 'No merchant found in the system for testing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.data['merchant'] = str(merchant.merchant_id)
        
        # Add username to the request data if not provided
        if 'username' not in request.data:
            # Generate username based on first name and national ID
            first_name = request.data.get('first_name', '').lower()
            national_id = request.data.get('national_id', '')
            if first_name and national_id:
                request.data['username'] = f"{first_name}_{national_id[-6:]}"
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet_request = serializer.save()
        
        # Send notification email
        wallet_request.send_notification_email()
        
        # PRODUCTION CODE: Normal flow would stop here and wait for approval
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        # TESTING CODE: Auto-approve and create wallet
        # Comment out this section when going to production
        username = wallet_request.username or f"customer_{wallet_request.national_id}"
        password = CustomUser.objects.make_random_password()
        user = CustomUser.objects.create_user(
            username=username,
            email=wallet_request.email,
            password=password,
            role='customer'
        )
        
        # Send password email
        self._send_password_email(wallet_request.email, user.username, password)
        
        # Create customer profile
        from security.models import CustomerUser
        customer = CustomerUser.objects.create(
            user=user,
            first_name=wallet_request.first_name,
            last_name=wallet_request.last_name,
            national_id=wallet_request.national_id,
            phone_number=wallet_request.phone_number,
            date_of_birth=wallet_request.date_of_birth,
            created_by=None  # No creator for auto-approval
        )
        
        # Create wallet
        wallet = Wallet.objects.create(
            user=user,
            merchant=wallet_request.merchant
        )
        
        # Update request status
        wallet_request.status = 'approved'
        wallet_request.processed_at = timezone.now()
        wallet_request.save()
        
        # Send updated notification email
        wallet_request.send_notification_email()
        
        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data
        response_data.update({
            'wallet_id': wallet.wallet_id,
            'username': user.username,
            'auto_approved': True
        })
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        # END TESTING CODE
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a wallet creation request"""
        wallet_request = self.get_object()
        
        if wallet_request.status != 'pending':
            return Response(
                {'error': 'This request has already been processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use provided username or generate one if not provided
        username = request.data.get('username')
        if not username:
            username = wallet_request.username or f"customer_{wallet_request.national_id}"
        
        # Create the customer user account with auto-generated password
        password = CustomUser.objects.make_random_password()
        user = CustomUser.objects.create_user(
            username=username,
            email=wallet_request.email,
            password=password,
            role='customer'
        )
        
        # Send password to customer via email
        self._send_password_email(wallet_request.email, user.username, password)
        
        # Create customer profile
        from security.models import CustomerUser
        customer = CustomerUser.objects.create(
            user=user,
            first_name=wallet_request.first_name,
            last_name=wallet_request.last_name,
            national_id=wallet_request.national_id,
            phone_number=wallet_request.phone_number,
            date_of_birth=wallet_request.date_of_birth,
            created_by=request.user
        )
        
        # Create the wallet
        wallet = Wallet.objects.create(
            user=user,
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
            'wallet_id': wallet.wallet_id,
            'username': user.username
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
        
    def _send_password_email(self, email, username, password):
        """Send initial password to customer via email"""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        
        context = {
            'username': username,
            'password': password,
            'login_url': settings.FRONTEND_URL + '/login' if hasattr(settings, 'FRONTEND_URL') else '/login'
        }
        
        subject = 'Welcome to Phantom Banking - Your Account Details'
        
        # Force use of the HTML template
        html_message = render_to_string('email/account_credentials.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message
        )
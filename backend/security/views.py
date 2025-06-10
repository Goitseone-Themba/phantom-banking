from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import MerchantProfile
from .serializers import (
    UserSerializer, MerchantProfileSerializer, MerchantSignupSerializer,
    LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    EmailVerificationSerializer, CreateWalletSerializer
)
from .auth_utils import (
    create_merchant_user, validate_login, send_verification_email,
    verify_email, send_password_reset_email, reset_password
)

User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def merchant_signup(self, request):
        serializer = MerchantSignupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user, merchant = create_merchant_user(**serializer.validated_data)
                return Response({
                    'message': 'Merchant account created successfully. Please check your email to verify your account.',
                    'user_id': user.id,
                    'merchant_id': merchant.id
                }, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            success, result = validate_login(
                serializer.validated_data['username_or_email'],
                serializer.validated_data['password']
            )
            
            if success:
                refresh = RefreshToken.for_user(result)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(result).data
                })
            return Response({'error': result}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            success, user = verify_email(serializer.validated_data['token'])
            if success:
                return Response({'message': 'Email verified successfully'})
            return Response({'error': 'Invalid or expired token'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def request_password_reset(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                send_password_reset_email(user, request)
                return Response({
                    'message': 'Password reset email sent successfully'
                })
            except User.DoesNotExist:
                # Return success even if email doesn't exist for security
                return Response({
                    'message': 'If an account exists with this email, a password reset link will be sent.'
                })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            success = reset_password(
                serializer.validated_data['token'],
                serializer.validated_data['new_password']
            )
            if success:
                return Response({'message': 'Password reset successfully'})
            return Response({'error': 'Invalid or expired token'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception:
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_400_BAD_REQUEST)

class MerchantViewSet(viewsets.ModelViewSet):
    queryset = MerchantProfile.objects.all()
    serializer_class = MerchantProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return MerchantProfile.objects.all()
        return MerchantProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_wallet(self, request):
        if request.user.role != 'merchant':
            return Response({'error': 'Only merchants can create wallets'},
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = CreateWalletSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Create customer user
                customer = User.objects.create_user(
                    username=f"customer_{serializer.validated_data['phone_number']}",
                    email=serializer.validated_data['email'],
                    password=User.objects.make_random_password(),  # Generate random password
                    first_name=serializer.validated_data['customer_name'].split()[0],
                    last_name=' '.join(serializer.validated_data['customer_name'].split()[1:]) 
                        if len(serializer.validated_data['customer_name'].split()) > 1 else '',
                    phone_number=serializer.validated_data['phone_number'],
                    role='customer'
                )
                
                # Send verification email with temporary password
                send_verification_email(customer)
                
                # Create wallet (assuming you have a Wallet model in the wallets app)
                from wallets.models import Wallet
                wallet = Wallet.objects.create(
                    user=customer,
                    merchant=request.user.merchant_profile,
                    balance=serializer.validated_data.get('initial_balance', 0)
                )
                
                return Response({
                    'message': 'Customer wallet created successfully. Verification email sent.',
                    'wallet_id': wallet.id
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({'error': str(e)}, 
                              status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if not user:
            # Increment failed login attempts
            try:
                user = User.objects.get(username=serializer.validated_data['username'])
                user.increment_failed_login()
            except User.DoesNotExist:
                pass

            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'error': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Reset failed login attempts on successful login
        user.reset_failed_login()

        # Update last login IP if provided
        if 'ip_address' in serializer.validated_data:
            user.last_login_ip = serializer.validated_data['ip_address']
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data['old_password']):
                return Response({
                    'old_password': 'Wrong password'
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data['new_password'])
            user.save()
            return Response({
                'message': 'Password updated successfully'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enable_two_factor(request):
    user = request.user
    if user.two_factor_enabled:
        return Response({
            'error': 'Two-factor authentication is already enabled'
        }, status=status.HTTP_400_BAD_REQUEST)

    # In a real implementation, this would generate and store a TOTP secret
    # and return a QR code for the user to scan
    import secrets
    user.two_factor_secret = secrets.token_hex(16)
    user.two_factor_enabled = True
    user.save()

    return Response({
        'message': 'Two-factor authentication enabled successfully',
        'secret': user.two_factor_secret  # In production, return QR code instead
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def disable_two_factor(request):
    user = request.user
    if not user.two_factor_enabled:
        return Response({
            'error': 'Two-factor authentication is not enabled'
        }, status=status.HTTP_400_BAD_REQUEST)

    user.two_factor_enabled = False
    user.two_factor_secret = ''
    user.save()

    return Response({
        'message': 'Two-factor authentication disabled successfully'
    })
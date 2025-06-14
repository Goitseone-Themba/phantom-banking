from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from dj_rest_auth.views import (
    LoginView as DefaultLoginView,
    LogoutView as DefaultLogoutView,
    UserDetailsView as DefaultUserDetailsView,
    PasswordChangeView as DefaultPasswordChangeView,
    PasswordResetView as DefaultPasswordResetView,
    PasswordResetConfirmView as DefaultPasswordResetConfirmView,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import EmailVerificationToken, LoginAttempt, UserSession
from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    UserDetailsSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer,
    LoginAttemptSerializer,
)
from .utils import get_client_ip, parse_user_agent

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint with email verification"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register a new user",
        description="Register a new user account with email verification",
        responses={
            201: OpenApiResponse(description="User created successfully"),
            400: OpenApiResponse(description="Validation errors"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user_id': str(user.id),
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(DefaultLoginView):
    """Custom login view with additional security features"""
    
    serializer_class = LoginSerializer
    
    @extend_schema(
        summary="User login",
        description="Authenticate user and return JWT tokens",
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials"),
            423: OpenApiResponse(description="Account locked"),
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Track successful login and create session record
        if response.status_code == 200 and hasattr(request, 'user'):
            user = request.user
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_info = parse_user_agent(user_agent)
            
            # Create or update user session
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.update_or_create(
                    user=user,
                    session_key=session_key,
                    defaults={
                        'ip_address': ip_address or '127.0.0.1',
                        'user_agent': user_agent,
                        'device_type': device_info['device_type'],
                        'browser': device_info['browser'],
                        'os': device_info['os'],
                        'is_active': True,
                    }
                )
        
        return response


class LogoutView(DefaultLogoutView):
    """Custom logout view"""
    
    @extend_schema(
        summary="User logout",
        description="Logout user and invalidate tokens",
        responses={
            200: OpenApiResponse(description="Logout successful"),
        }
    )
    def post(self, request, *args, **kwargs):
        # Deactivate user session
        if hasattr(request, 'user') and request.user.is_authenticated:
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.filter(
                    user=request.user,
                    session_key=session_key
                ).update(is_active=False)
        
        return super().post(request, *args, **kwargs)


class UserDetailsView(DefaultUserDetailsView):
    """Extended user details view"""
    
    serializer_class = UserDetailsSerializer
    
    @extend_schema(
        summary="Get user details",
        description="Get authenticated user's profile information",
        responses={
            200: UserDetailsSerializer,
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user details",
        description="Update authenticated user's profile information",
        responses={
            200: UserDetailsSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update user details",
        description="Partially update authenticated user's profile information",
        responses={
            200: UserDetailsSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class EmailVerificationView(APIView):
    """Email verification endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Verify email address",
        description="Verify user's email address using verification token",
        request=EmailVerificationSerializer,
        responses={
            200: OpenApiResponse(description="Email verified successfully"),
            400: OpenApiResponse(description="Invalid or expired token"),
        }
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Email verified successfully.',
                'user_id': str(user.id),
                'email': user.email
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    """Resend email verification endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Resend verification email",
        description="Resend email verification link to user's email",
        request=ResendVerificationSerializer,
        responses={
            200: OpenApiResponse(description="Verification email sent"),
            400: OpenApiResponse(description="Email already verified or not found"),
        }
    )
    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Verification email sent successfully.',
                'email': user.email
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(DefaultPasswordChangeView):
    """Custom password change view"""
    
    serializer_class = PasswordChangeSerializer
    
    @extend_schema(
        summary="Change password",
        description="Change authenticated user's password",
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PasswordResetView(DefaultPasswordResetView):
    """Custom password reset view"""
    
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Request password reset",
        description="Send password reset email to user",
        responses={
            200: OpenApiResponse(description="Password reset email sent"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PasswordResetConfirmView(DefaultPasswordResetConfirmView):
    """Custom password reset confirmation view"""
    
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Confirm password reset",
        description="Reset password using reset token",
        responses={
            200: OpenApiResponse(description="Password reset successfully"),
            400: OpenApiResponse(description="Invalid or expired token"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management view"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get user profile",
        description="Get authenticated user's profile information",
        responses={
            200: UserProfileSerializer,
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update authenticated user's profile information",
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update user profile",
        description="Partially update authenticated user's profile information",
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class LoginAttemptsView(generics.ListAPIView):
    """View user's login attempts for security monitoring"""
    
    serializer_class = LoginAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LoginAttempt.objects.filter(
            user=self.request.user
        ).order_by('-attempted_at')[:20]  # Last 20 attempts
    
    @extend_schema(
        summary="Get login attempts",
        description="Get authenticated user's recent login attempts",
        responses={
            200: LoginAttemptSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ActiveSessionsView(APIView):
    """View and manage user's active sessions"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get active sessions",
        description="Get authenticated user's active sessions",
        responses={
            200: OpenApiResponse(description="List of active sessions"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def get(self, request):
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-last_activity')
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session.id),
                'ip_address': session.ip_address,
                'device_type': session.device_type,
                'browser': session.browser,
                'os': session.os,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'is_current': session.session_key == request.session.session_key
            })
        
        return Response({'sessions': sessions_data})
    
    @extend_schema(
        summary="Terminate session",
        description="Terminate a specific user session",
        parameters=[
            OpenApiParameter(
                name='session_id',
                description='Session ID to terminate',
                required=True,
                type=str
            )
        ],
        responses={
            200: OpenApiResponse(description="Session terminated"),
            400: OpenApiResponse(description="Invalid session ID"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def delete(self, request):
        session_id = request.data.get('session_id')
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=request.user,
                is_active=True
            )
            session.deactivate()
            return Response({'message': 'Session terminated successfully'})
        except UserSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    summary="Check authentication status",
    description="Check if user is authenticated and return basic info",
    responses={
        200: OpenApiResponse(description="Authentication status"),
    }
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_status(request):
    """Check authentication status"""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': str(request.user.id),
                'email': request.user.email,
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'user_type': request.user.user_type,
                'is_email_verified': request.user.is_email_verified,
            }
        })
    else:
        return Response({'authenticated': False})


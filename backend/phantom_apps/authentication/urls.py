from django.urls import path, include
from dj_rest_auth.registration.views import (
    RegisterView as DefaultRegisterView,
    VerifyEmailView as DefaultVerifyEmailView,
    ResendEmailVerificationView as DefaultResendEmailVerificationView,
)
from .views import (
    UserRegistrationView,
    LoginView,
    LogoutView,
    UserDetailsView,
    EmailVerificationView,
    ResendVerificationView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    UserProfileView,
    LoginAttemptsView,
    ActiveSessionsView,
    auth_status,
)

app_name = 'authentication'

urlpatterns = [
    # Authentication status
    path('status/', auth_status, name='auth_status'),
    
    # Registration and email verification
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),
    
    # Login/Logout
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User profile and details
    path('user/', UserDetailsView.as_view(), name='user_details'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Security and monitoring
    path('login-attempts/', LoginAttemptsView.as_view(), name='login_attempts'),
    path('sessions/', ActiveSessionsView.as_view(), name='active_sessions'),
    
    # Include dj-rest-auth URLs for additional endpoints
    # (Optional: provides token endpoints and some additional features)
    # path('', include('dj_rest_auth.urls')),
]


from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import Merchant
from .serializers import MerchantRegistrationSerializer
from security.models import MerchantUser
from security.auth_utils import send_verification_email

User = get_user_model()

class MerchantRegistrationView(APIView):
    """
    View for merchant registration without authentication
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
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
                merchant_profile = MerchantUser.objects.create(
                    user=user,
                    business_name=data['business_name'],
                    registration_number=data['registration_number'],
                    contact_email=data['contact_email'],
                    contact_phone=data['contact_phone'],
                    business_type='standard',
                    address=''
                )
                
                # Send verification email
                send_verification_email(user)
                
                return Response({
                    'message': 'Merchant account created successfully. Please check your email to verify your account.',
                    'user_id': user.id,
                    'merchant_id': merchant.merchant_id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
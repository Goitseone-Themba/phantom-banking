from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .authentication import get_tokens_for_user
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        operation_description="Register a new user (merchant or admin)",
        responses={201: UserRegistrationSerializer()}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({
                'user': serializer.data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        operation_description="Login with username and password",
        responses={200: openapi.Response(
            description="Login successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'tokens': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        )}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user:
                tokens = get_tokens_for_user(user)
                return Response({
                    'tokens': tokens,
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'business_name': user.business_name
                    }
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_protected_view(request):
    """
    A test protected view that requires authentication
    """
    return Response({
        'message': 'You have access to this protected endpoint',
        'user': request.user.username,
        'email': request.user.email,
        'role': request.user.role
    })
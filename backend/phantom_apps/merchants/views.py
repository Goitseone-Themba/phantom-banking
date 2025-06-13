from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from .models import Merchant, APICredential
from .serializers import MerchantRegistrationSerializer, MerchantSerializer, APICredentialSerializer
import logging

logger = logging.getLogger('phantom_apps')

class MerchantViewSet(viewsets.ModelViewSet):
    """ViewSet for merchant operations"""
    
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter merchants by authenticated user"""
        return Merchant.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """Register a new merchant"""
        serializer = MerchantRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            merchant = serializer.save()
            logger.info(f"New merchant registered: {merchant.business_name}")
            return Response({
                'message': 'Merchant registered successfully',
                'merchant_id': merchant.merchant_id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get merchant dashboard data"""
        try:
            merchant = request.user.merchant
            # Add dashboard logic here
            dashboard_data = {
                'merchant': MerchantSerializer(merchant).data,
                'total_wallets': 0,  # Add wallet count
                'total_transactions': 0,  # Add transaction count
                'total_volume': 0,  # Add transaction volume
            }
            return Response(dashboard_data)
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'Merchant not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def generate_api_credentials(self, request):
        """Generate new API credentials for merchant"""
        try:
            merchant = request.user.merchant
            # Add API credential generation logic here
            return Response({
                'message': 'API credentials generated successfully'
            })
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'Merchant not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

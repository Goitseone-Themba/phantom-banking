from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Customer
from .serializers import CustomerSerializer, CustomerCreateSerializer
from ..common.permissions import IsMerchantOwner
import logging

logger = logging.getLogger('phantom_apps')

class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for customer operations"""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter customers by merchant"""
        try:
            return Customer.objects.filter(merchant=self.request.user.merchant)
        except:
            return Customer.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerCreateSerializer
        return CustomerSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new customer"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            logger.info(f"New customer created: {customer.first_name} {customer.last_name}")
            return Response(
                CustomerSerializer(customer).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

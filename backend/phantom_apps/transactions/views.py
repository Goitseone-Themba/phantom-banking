import json
import qrcode
import io
import base64
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import QRCode, EFTPayment, Transaction
from .serializers import (
    QRCodeCreateSerializer, QRCodeSerializer, QRCodePaymentSerializer,
    EFTPaymentSerializer, EFTPaymentCreateSerializer,
    TransactionSerializer
)
from ..merchants.models import Merchant
from ..customers.models import Customer
from ..wallets.models import Wallet
from .services import EFTPaymentService, QRCodeService


class QRCodeCreateView(generics.CreateAPIView):
    """Create QR Code for payment"""
    serializer_class = QRCodeCreateSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Create QR Code for Payment",
        description="Generate a QR code that customers can scan to make payments",
        responses={201: QRCodeSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            qr_code = QRCodeService.create_qr_code(
                merchant_id=serializer.validated_data['merchant_id'],
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data.get('description', ''),
                reference=serializer.validated_data.get('reference', ''),
                expires_in_minutes=serializer.validated_data.get('expires_in_minutes', 15)
            )
            
            response_serializer = QRCodeSerializer(qr_code)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class QRCodeDetailView(generics.RetrieveAPIView):
    """Get QR Code details"""
    serializer_class = QRCodeSerializer
    permission_classes = [AllowAny]
    lookup_field = 'qr_token'
    
    def get_queryset(self):
        return QRCode.objects.select_related('merchant', 'customer', 'transaction')
    
    @extend_schema(
        summary="Get QR Code Details",
        description="Retrieve QR code information by token",
        parameters=[
            OpenApiParameter(
                name='qr_token',
                description='QR Code token',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Process QR Code Payment",
    description="Process payment using QR code token",
    request=QRCodePaymentSerializer,
    responses={200: TransactionSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def process_qr_payment(request, qr_token):
    """Process QR code payment"""
    try:
        # Get QR code
        qr_code = QRCode.objects.select_related('merchant').get(qr_token=qr_token)
        
        if not qr_code.is_valid:
            return Response(
                {'error': 'QR code is invalid or expired'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = QRCodePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process payment
        with transaction.atomic():
            transaction_obj = QRCodeService.process_qr_payment(
                qr_code=qr_code,
                customer_phone=serializer.validated_data['customer_phone'],
                wallet_id=serializer.validated_data.get('wallet_id')
            )
            
            response_serializer = TransactionSerializer(transaction_obj)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
    except QRCode.DoesNotExist:
        return Response(
            {'error': 'QR code not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class EFTPaymentCreateView(generics.CreateAPIView):
    """Initiate EFT payment for wallet top-up"""
    serializer_class = EFTPaymentCreateSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Initiate EFT Payment",
        description="Start EFT payment process for wallet top-up",
        responses={201: EFTPaymentSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                eft_payment = EFTPaymentService.initiate_eft_payment(
                    customer_phone=serializer.validated_data['customer_phone'],
                    wallet_id=serializer.validated_data['wallet_id'],
                    amount=serializer.validated_data['amount'],
                    bank_code=serializer.validated_data['bank_code'],
                    account_number=serializer.validated_data['account_number'],
                    reference=serializer.validated_data.get('reference', '')
                )
                
                response_serializer = EFTPaymentSerializer(eft_payment)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class EFTPaymentStatusView(generics.RetrieveAPIView):
    """Check EFT payment status"""
    serializer_class = EFTPaymentSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return EFTPayment.objects.select_related('customer', 'wallet', 'transaction')
    
    @extend_schema(
        summary="Check EFT Payment Status",
        description="Get current status of EFT payment",
        parameters=[
            OpenApiParameter(
                name='id',
                description='EFT Payment ID',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="EFT Webhook Handler",
    description="Handle EFT payment status updates from bank",
    request=OpenApiTypes.OBJECT,
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def eft_webhook_handler(request):
    """Handle EFT payment webhooks from banks"""
    try:
        # Extract webhook data
        webhook_data = request.data
        external_reference = webhook_data.get('reference')
        status_update = webhook_data.get('status')
        
        if not external_reference:
            return Response(
                {'error': 'Missing reference'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process webhook
        with transaction.atomic():
            result = EFTPaymentService.process_webhook(
                external_reference=external_reference,
                webhook_data=webhook_data
            )
            
            return Response({
                'status': 'success',
                'processed': result
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class TransactionListView(generics.ListAPIView):
    """List transactions with filtering"""
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Transaction.objects.select_related(
            'customer', 'merchant', 'from_wallet', 'to_wallet'
        )
        
        # Filter by customer
        customer_phone = self.request.query_params.get('customer_phone')
        if customer_phone:
            queryset = queryset.filter(customer__phone_number=customer_phone)
        
        # Filter by merchant
        merchant_id = self.request.query_params.get('merchant_id')
        if merchant_id:
            queryset = queryset.filter(merchant_id=merchant_id)
        
        # Filter by type
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset[:100]  # Limit results
    
    @extend_schema(
        summary="List Transactions",
        description="Get list of transactions with optional filtering",
        parameters=[
            OpenApiParameter('customer_phone', OpenApiTypes.STR, description='Filter by customer phone'),
            OpenApiParameter('merchant_id', OpenApiTypes.UUID, description='Filter by merchant ID'),
            OpenApiParameter('type', OpenApiTypes.STR, description='Filter by transaction type'),
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Get QR Code Image",
    description="Generate QR code image for scanning",
    responses={200: OpenApiTypes.BINARY}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_qr_image(request, qr_token):
    """Generate QR code image"""
    try:
        qr_code_obj = QRCode.objects.get(qr_token=qr_token)
        
        if not qr_code_obj.is_valid:
            return Response(
                {'error': 'QR code is invalid or expired'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate QR code image
        qr_img = QRCodeService.generate_qr_image(qr_code_obj.qr_data)
        
        # Return image as base64
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        return Response({
            'qr_token': qr_token,
            'image': f"data:image/png;base64,{img_str}",
            'expires_at': qr_code_obj.expires_at
        })
        
    except QRCode.DoesNotExist:
        return Response(
            {'error': 'QR code not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
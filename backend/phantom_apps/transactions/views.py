import json
import io
import base64
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework import status, viewsets, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..common.exceptions import (
    PhantomBankingException,
    PhantomBankingErrorCodes,
    WalletNotFoundError,
    InsufficientFundsError
)
from .serializers import (
    TransactionSerializer,
    TransactionListSerializer,
    TransactionCreateSerializer,
    TransactionResponseSerializer,
    QRPaymentSerializer,
    EFTPaymentSerializer,
    EFTMerchantPaymentSerializer,
    QRCodeCreateSerializer,
    QRCodeSerializer,
    QRCodePaymentSerializer,
    EFTPaymentCreateSerializer,
    TransactionSummarySerializer,
    EFTWebhookSerializer
)
from .services import TransactionService, QRCodeService, EFTPaymentService, PaymentAnalyticsService
from .models import Transaction, QRCode, EFTPayment
import logging

logger = logging.getLogger('phantom_apps')


# =============================================================================
# Merchant-Authenticated Transaction Views (from approach 1)
# =============================================================================

@extend_schema(
    tags=['Merchant Transactions'],
    summary='Process a QR code payment',
    description='''
    Process a payment using QR code (merchant perspective).
    
    **Business Rules:**
    - Customer must have sufficient wallet balance
    - Transaction must be properly referenced
    - QR code must be valid
    ''',
    request=QRPaymentSerializer,
    responses={
        201: TransactionResponseSerializer,
        400: {
            'description': 'Bad Request',
            'example': {
                'error': True,
                'error_code': 'INVALID_TRANSACTION_DATA',
                'message': 'Invalid transaction data',
                'status_code': 400
            }
        },
        404: {
            'description': 'Wallet Not Found',
            'example': {
                'error': True,
                'error_code': 'WALLET_NOT_FOUND',
                'message': 'Wallet with specified ID not found',
                'status_code': 404
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_qr_payment_merchant(request):
    """
    Process a payment using QR code (merchant perspective)
    
    URL: POST /api/v1/transactions/qr-payment/
    """
    try:
        # Extract merchant from JWT token
        try:
            merchant = request.user.merchant
        except AttributeError:
            logger.error(f"User {request.user.username} has no associated merchant")
            return Response({
                'error': True,
                'error_code': PhantomBankingErrorCodes.MERCHANT_NOT_FOUND,
                'message': 'No merchant associated with authenticated user',
                'status_code': 403
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate request data
        serializer = QRPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': True,
                'error_code': PhantomBankingErrorCodes.INVALID_TRANSACTION_DATA,
                'message': 'Invalid request data',
                'details': serializer.errors,
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process payment using service
        transaction_data = serializer.validated_data
        transaction_obj = TransactionService.process_qr_payment(
            merchant=merchant,
            wallet_id=transaction_data['wallet_id'],
            amount=transaction_data['amount'],
            qr_code=transaction_data['qr_code'],
            reference=transaction_data.get('reference'),
            description=transaction_data.get('description')
        )
        
        # Serialize response
        response_serializer = TransactionResponseSerializer(transaction_obj)
        
        response_data = {
            'success': True,
            'message': 'QR Payment processed successfully',
            'transaction': response_serializer.data,
            'status_code': 201
        }
        
        logger.info(f"QR Payment successful - Merchant: {merchant.merchant_id}, Transaction: {transaction_obj.transaction_id}")
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except WalletNotFoundError as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except InsufficientFundsError as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except PhantomBankingException as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except Exception as e:
        logger.error(f"Unexpected error in QR payment processing: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.TRANSACTION_FAILED,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Merchant Transactions'],
    summary='Process an EFT payment',
    description='''
    Process a payment using EFT (Electronic Fund Transfer) (merchant perspective).
    
    **Business Rules:**
    - Customer must have sufficient wallet balance
    - Transaction must be properly referenced
    - Bank details must be valid
    ''',
    request=EFTPaymentSerializer,
    responses={201: TransactionResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_eft_payment_merchant(request):
    """
    Process a payment using EFT (merchant perspective)
    
    URL: POST /api/v1/transactions/eft-payment/
    """
    try:
        # Extract merchant from JWT token
        try:
            merchant = request.user.merchant
        except AttributeError:
            logger.error(f"User {request.user.username} has no associated merchant")
            return Response({
                'error': True,
                'error_code': PhantomBankingErrorCodes.MERCHANT_NOT_FOUND,
                'message': 'No merchant associated with authenticated user',
                'status_code': 403
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate request data
        serializer = EFTMerchantPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': True,
                'error_code': PhantomBankingErrorCodes.INVALID_TRANSACTION_DATA,
                'message': 'Invalid request data',
                'details': serializer.errors,
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process payment using service
        transaction_data = serializer.validated_data
        transaction_obj = TransactionService.process_eft_payment(
            merchant=merchant,
            wallet_id=transaction_data['wallet_id'],
            amount=transaction_data['amount'],
            bank_name=transaction_data['bank_name'],
            account_number=transaction_data['account_number'],
            reference=transaction_data.get('reference'),
            description=transaction_data.get('description')
        )
        
        # Serialize response
        response_serializer = TransactionResponseSerializer(transaction_obj)
        
        response_data = {
            'success': True,
            'message': 'EFT Payment processed successfully',
            'transaction': response_serializer.data,
            'status_code': 201
        }
        
        logger.info(f"EFT Payment successful - Merchant: {merchant.merchant_id}, Transaction: {transaction_obj.transaction_id}")
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except (WalletNotFoundError, InsufficientFundsError, PhantomBankingException) as e:
        return Response({
            'error': True,
            'error_code': e.error_code,
            'message': e.message,
            'status_code': e.status_code
        }, status=e.status_code)
        
    except Exception as e:
        logger.error(f"Unexpected error in EFT payment processing: {e}")
        return Response({
            'error': True,
            'error_code': PhantomBankingErrorCodes.TRANSACTION_FAILED,
            'message': 'Internal server error occurred',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MerchantTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for merchant transaction history and details
    Allows merchants to retrieve transaction history for their wallets
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter transactions by merchant and optionally by wallet"""
        try:
            merchant = self.request.user.merchant
            queryset = Transaction.objects.filter(merchant=merchant).order_by('-created_at')
            
            # Filter by wallet_id if provided
            wallet_id = self.request.query_params.get('wallet_id')
            if wallet_id:
                queryset = queryset.filter(wallet__wallet_id=wallet_id)
                
            # Filter by transaction_type if provided
            transaction_type = self.request.query_params.get('transaction_type')
            if transaction_type:
                queryset = queryset.filter(transaction_type=transaction_type)
                
            # Filter by status if provided
            status_code = self.request.query_params.get('status')
            if status_code:
                queryset = queryset.filter(status__code=status_code)
                
            # Filter by date range if provided
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            if start_date and end_date:
                queryset = queryset.filter(created_at__range=[start_date, end_date])
                
            return queryset
        except AttributeError:
            return Transaction.objects.none()
            
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary statistics for a merchant"""
        try:
            merchant = request.user.merchant
            summary = TransactionService.get_transaction_summary(merchant)
            return Response(summary)
        except Exception as e:
            logger.error(f"Error generating transaction summary: {e}")
            return Response(
                {'error': 'Failed to generate transaction summary'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============================================================================
# Public QR Code and EFT Payment Views (from approach 2)
# =============================================================================

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
def process_qr_payment_public(request, qr_token):
    """Process QR code payment (public endpoint)"""
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
    request=EFTWebhookSerializer,
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def eft_webhook_handler(request):
    """Handle EFT payment webhooks from banks"""
    try:
        # Validate webhook data
        serializer = EFTWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract webhook data
        webhook_data = serializer.validated_data
        external_reference = webhook_data.get('reference')
        
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
    serializer_class = TransactionListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Transaction.objects.select_related(
            'customer', 'merchant', 'from_wallet', 'to_wallet', 'status', 'payment_method'
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
            queryset = queryset.filter(status__code=status_filter)
        
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


# =============================================================================
# Analytics and Reporting Views
# =============================================================================

@extend_schema(
    summary="Get Payment Analytics",
    description="Get payment analytics and summary statistics",
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def payment_analytics(request):
    """Get payment analytics"""
    try:
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        merchant_id = request.query_params.get('merchant_id')
        
        summary = PaymentAnalyticsService.get_payment_summary(
            date_from=date_from,
            date_to=date_to,
            merchant_id=merchant_id
        )
        
        return Response(summary, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating payment analytics: {e}")
        return Response(
            {'error': 'Failed to generate analytics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
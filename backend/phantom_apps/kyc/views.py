from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import json
import logging


from .swagger_schemas import (
    kyc_start_verification_swagger, 
    kyc_summary_swagger, 
    kyc_status_swagger,
    veriff_webhook_swagger
)

from .models import KYCRecord, KYCDocument, KYCEvent
from .serializers import (
    KYCRecordSerializer, 
    KYCStartVerificationSerializer,
    KYCDocumentSerializer,
    KYCEventSerializer
)
from .services.veriff_service import VeriffService

logger = logging.getLogger(__name__)


class KYCRecordViewSet(ModelViewSet):
    """
    ViewSet for managing KYC records
    """
    serializer_class = KYCRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return KYCRecord.objects.all()
        return KYCRecord.objects.filter(user=self.request.user)

    @kyc_start_verification_swagger()
    @action(detail=False, methods=['post'])
    def start_verification(self, request):
        """Start KYC verification process"""
        try:
            # Check if user already has a KYC record
            existing_record = KYCRecord.objects.filter(user=request.user).first()
            
            if existing_record:
                if existing_record.status == KYCRecord.Status.APPROVED:
                    return Response({
                        'error': 'KYC already verified',
                        'kyc_record': KYCRecordSerializer(existing_record).data
                    }, status=status.HTTP_400_BAD_REQUEST)
                elif existing_record.status == KYCRecord.Status.IN_PROGRESS:
                    return Response({
                        'error': 'KYC verification already in progress',
                        'session_url': existing_record.veriff_session_url,
                        'kyc_record': KYCRecordSerializer(existing_record).data
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Validate input data
            serializer = KYCStartVerificationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Create or update KYC record
            if existing_record:
                # Update existing record with new data
                for field, value in serializer.validated_data.items():
                    setattr(existing_record, field, value)
                existing_record.status = KYCRecord.Status.PENDING
                existing_record.save()
                kyc_record = existing_record
            else:
                # Create new KYC record
                kyc_record = KYCRecord.objects.create(
                    user=request.user,
                    **serializer.validated_data
                )

            # Create Veriff session
            veriff_service = VeriffService()
            success, result = veriff_service.create_verification_session(kyc_record)

            if success:
                return Response({
                    'message': 'Verification session created successfully',
                    'session_url': result['session_url'],
                    'session_id': result['session_id'],
                    'kyc_record': KYCRecordSerializer(kyc_record).data
                }, status=status.HTTP_201_CREATED)
            else:
                kyc_record.delete()  # Clean up if session creation failed
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error starting KYC verification: {str(e)}")
            return Response({
                'error': 'An error occurred while starting verification'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @kyc_status_swagger()
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get KYC status and session information"""
        kyc_record = self.get_object()
        
        # If there's a Veriff session, get latest status
        if kyc_record.veriff_session_id:
            veriff_service = VeriffService()
            success, result = veriff_service.get_session_status(kyc_record.veriff_session_id)
            
            if success:
                # Update local record if needed
                verification = result.get('verification', {})
                decision = verification.get('decision')
                if decision and decision != kyc_record.veriff_decision:
                    kyc_record.veriff_decision = decision
                    kyc_record.veriff_code = verification.get('code')
                    kyc_record.veriff_reason = verification.get('reason')
                    
                    if decision == 'approved' and kyc_record.status != KYCRecord.Status.APPROVED:
                        kyc_record.approve()
                    elif decision == 'declined' and kyc_record.status != KYCRecord.Status.REJECTED:
                        kyc_record.reject(reason=verification.get('reason'))

        return Response(KYCRecordSerializer(kyc_record).data)

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get KYC events/history"""
        kyc_record = self.get_object()
        events = kyc_record.events.all()
        serializer = KYCEventSerializer(events, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class VeriffWebhookView(APIView):
    """
    Handle webhooks from Veriff
    """
    permission_classes = []  # No authentication required for webhooks
    @veriff_webhook_swagger()
    def post(self, request):
        try:
            # Get signature from headers
            signature = request.META.get('HTTP_X_VERIFF_SIGNATURE', '')
            
            # Process webhook
            veriff_service = VeriffService()
            success = veriff_service.handle_webhook(request.data, signature)
            
            if success:
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error processing Veriff webhook: {str(e)}")
            return Response({'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@kyc_summary_swagger()
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def kyc_summary(request):
    """Get KYC summary for the current user"""
    try:
        kyc_record = KYCRecord.objects.get(user=request.user)
        
        # Get user's wallet info if available
        wallet_info = None
        try:
            # Assuming you have a Wallet model - adjust import as needed
            from ..wallets.models import Wallet
            wallet = Wallet.objects.get(user=request.user)
            wallet_info = {
                'wallet_type': getattr(wallet, 'wallet_type', 'basic'),
                'balance': str(getattr(wallet, 'balance', 0)),
                'can_upgrade': not kyc_record.is_verified
            }
        except:
            pass
        
        return Response({
            'kyc_status': kyc_record.status,
            'is_verified': kyc_record.is_verified,
            'verification_level': kyc_record.verification_level,
            'created_at': kyc_record.created_at,
            'verified_at': kyc_record.verified_at,
            'expires_at': kyc_record.expires_at,
            'wallet_info': wallet_info
        })
        
    except KYCRecord.DoesNotExist:
        return Response({
            'kyc_status': 'not_started',
            'is_verified': False,
            'message': 'KYC verification not started'
        })
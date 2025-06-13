
import requests
import hashlib
import hmac
import json
import logging
from django.conf import settings
from django.utils import timezone
from typing import Dict, Optional, Tuple
from ..models import KYCRecord, KYCEvent

logger = logging.getLogger(__name__)

class VeriffService:
    """
    Service class for integrating with Veriff KYC verification API
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'VERIFF_API_KEY', '')
        self.api_secret = getattr(settings, 'VERIFF_API_SECRET', '')
        self.base_url = getattr(settings, 'VERIFF_BASE_URL', 'https://stationapi.veriff.com')
        self.webhook_secret = getattr(settings, 'VERIFF_WEBHOOK_SECRET', '')
        
        if not all([self.api_key, self.api_secret]):
            logger.error("Veriff API credentials not configured")

    def create_verification_session(self, kyc_record: KYCRecord) -> Tuple[bool, Dict]:
        """
        Create a new verification session with Veriff
        """
        url = f"{self.base_url}/v1/sessions"
        
        payload = {
            "verification": {
                "callback": f"{settings.FRONTEND_URL}/kyc/callback",
                "person": {
                    "firstName": kyc_record.first_name,
                    "lastName": kyc_record.last_name,
                    "idNumber": kyc_record.document_number if kyc_record.document_number else None,
                    "dateOfBirth": kyc_record.date_of_birth.isoformat() if kyc_record.date_of_birth else None,
                },
                "document": {
                    "number": kyc_record.document_number if kyc_record.document_number else None,
                    "type": self._map_document_type(kyc_record.document_type),
                    "country": kyc_record.nationality if kyc_record.nationality else "BW",
                },
                "vendorData": str(kyc_record.id),  # Our internal reference
                "timestamp": timezone.now().isoformat(),
            }
        }

        try:
            headers = self._get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 201:
                data = response.json()
                verification = data.get('verification', {})
                
                # Update KYC record with Veriff session details
                kyc_record.veriff_session_id = verification.get('id')
                kyc_record.veriff_session_url = verification.get('url')
                kyc_record.status = KYCRecord.Status.IN_PROGRESS
                kyc_record.save()
                
                # Log event
                KYCEvent.objects.create(
                    kyc_record=kyc_record,
                    event_type=KYCEvent.EventType.SESSION_CREATED,
                    description=f"Veriff session created: {verification.get('id')}",
                    metadata={"session_id": verification.get('id'), "session_url": verification.get('url')}
                )
                
                logger.info(f"Created Veriff session for user {kyc_record.user.id}: {verification.get('id')}")
                return True, {"session_url": verification.get('url'), "session_id": verification.get('id')}
            
            else:
                logger.error(f"Failed to create Veriff session: {response.status_code} - {response.text}")
                return False, {"error": "Failed to create verification session"}
                
        except requests.RequestException as e:
            logger.error(f"Network error creating Veriff session: {str(e)}")
            return False, {"error": "Network error occurred"}
        except Exception as e:
            logger.error(f"Unexpected error creating Veriff session: {str(e)}")
            return False, {"error": "An unexpected error occurred"}

    def get_session_status(self, session_id: str) -> Tuple[bool, Dict]:
        """
        Get the current status of a verification session
        """
        url = f"{self.base_url}/v1/sessions/{session_id}"
        
        try:
            headers = self._get_headers()
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                logger.error(f"Failed to get session status: {response.status_code} - {response.text}")
                return False, {"error": "Failed to get session status"}
                
        except requests.RequestException as e:
            logger.error(f"Network error getting session status: {str(e)}")
            return False, {"error": "Network error occurred"}

    def handle_webhook(self, payload: Dict, signature: str) -> bool:
        """
        Handle incoming webhook from Veriff
        """
        # Verify webhook signature
        if not self._verify_webhook_signature(payload, signature):
            logger.error("Invalid webhook signature")
            return False

        verification_id = payload.get('id')
        if not verification_id:
            logger.error("No verification ID in webhook payload")
            return False

        try:
            # Find KYC record by Veriff session ID
            kyc_record = KYCRecord.objects.get(veriff_session_id=verification_id)
            
            # Update KYC record based on webhook data
            decision = payload.get('verification', {}).get('decision')
            code = payload.get('verification', {}).get('code')
            reason = payload.get('verification', {}).get('reason')
            
            kyc_record.veriff_decision = decision
            kyc_record.veriff_code = code
            kyc_record.veriff_reason = reason
            
            # Map Veriff decision to our status
            if decision == 'approved':
                kyc_record.approve()
                event_type = KYCEvent.EventType.APPROVED
                description = "KYC verification approved by Veriff"
                
                # Trigger wallet upgrade
                self._trigger_wallet_upgrade(kyc_record)
                
            elif decision == 'declined':
                kyc_record.reject(reason=reason)
                event_type = KYCEvent.EventType.REJECTED
                description = f"KYC verification rejected by Veriff: {reason}"
                
            else:  # resubmission_requested or other
                kyc_record.status = KYCRecord.Status.RESUBMISSION_REQUESTED
                kyc_record.save()
                event_type = KYCEvent.EventType.VERIFICATION_COMPLETED
                description = f"KYC verification requires resubmission: {reason}"

            # Log event
            KYCEvent.objects.create(
                kyc_record=kyc_record,
                event_type=event_type,
                description=description,
                metadata=payload
            )
            
            logger.info(f"Processed webhook for KYC record {kyc_record.id}: {decision}")
            return True
            
        except KYCRecord.DoesNotExist:
            logger.error(f"KYC record not found for verification ID: {verification_id}")
            return False
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for Veriff API requests"""
        return {
            'X-AUTH-CLIENT': self.api_key,
            'Content-Type': 'application/json',
        }

    def _map_document_type(self, doc_type: str) -> str:
        """Map our document types to Veriff's expected types"""
        mapping = {
            'passport': 'PASSPORT',
            'id_card': 'ID_CARD',
            'driving_license': 'DRIVERS_LICENSE',
        }
        return mapping.get(doc_type, 'PASSPORT')

    def _verify_webhook_signature(self, payload: Dict, signature: str) -> bool:
        """Verify that the webhook came from Veriff"""
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping signature verification")
            return True
            
        payload_string = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    def _trigger_wallet_upgrade(self, kyc_record: KYCRecord):
        """Trigger wallet upgrade after successful KYC"""
        try:
            # Import here to avoid circular imports
            from ..services.wallet_service import WalletService
            
            wallet_service = WalletService()
            wallet_service.upgrade_wallet_after_kyc(kyc_record.user)
            
        except Exception as e:
            logger.error(f"Failed to trigger wallet upgrade for user {kyc_record.user.id}: {str(e)}")

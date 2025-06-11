from django.core.management.base import BaseCommand
from django.utils import timezone
from phantom_apps.kyc.models import KYCRecord
from phantom_apps.kyc.services.veriff_service import VeriffService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check and update KYC status for pending verifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Check specific user ID only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting KYC status check...')
        
        # Get pending KYC records
        queryset = KYCRecord.objects.filter(
            status__in=[KYCRecord.Status.PENDING, KYCRecord.Status.IN_PROGRESS],
            veriff_session_id__isnull=False
        )
        
        if options['user_id']:
            queryset = queryset.filter(user_id=options['user_id'])
        
        if not queryset.exists():
            self.stdout.write(self.style.WARNING('No pending KYC records found'))
            return
        
        veriff_service = VeriffService()
        updated_count = 0
        
        for kyc_record in queryset:
            self.stdout.write(f'Checking KYC for user {kyc_record.user.username}...')
            
            try:
                success, result = veriff_service.get_session_status(kyc_record.veriff_session_id)
                
                if success:
                    verification = result.get('verification', {})
                    decision = verification.get('decision')
                    
                    if decision and decision != kyc_record.veriff_decision:
                        if not options['dry_run']:
                            kyc_record.veriff_decision = decision
                            kyc_record.veriff_code = verification.get('code')
                            kyc_record.veriff_reason = verification.get('reason')
                            
                            if decision == 'approved':
                                kyc_record.approve()
                                self.stdout.write(
                                    self.style.SUCCESS(f'✅ Approved KYC for {kyc_record.user.username}')
                                )
                            elif decision == 'declined':
                                kyc_record.reject(reason=verification.get('reason'))
                                self.stdout.write(
                                    self.style.ERROR(f'❌ Rejected KYC for {kyc_record.user.username}')
                                )
                            else:
                                kyc_record.status = KYCRecord.Status.RESUBMISSION_REQUESTED
                                kyc_record.save()
                                self.stdout.write(
                                    self.style.WARNING(f'⚠️  Resubmission required for {kyc_record.user.username}')
                                )
                            
                            updated_count += 1
                        else:
                            self.stdout.write(f'Would update {kyc_record.user.username}: {decision}')
                    else:
                        self.stdout.write(f'No status change for {kyc_record.user.username}')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to check status for {kyc_record.user.username}: {result}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error checking {kyc_record.user.username}: {str(e)}')
                )
                logger.error(f'Error in check_kyc_status command: {str(e)}')
        
        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS('Dry run completed'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'KYC status check completed. Updated {updated_count} records.')
            )
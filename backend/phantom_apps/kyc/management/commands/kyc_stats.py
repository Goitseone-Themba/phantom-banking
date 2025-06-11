from django.core.management.base import BaseCommand
from django.db.models import Count
from phantom_apps.kyc.models import KYCRecord
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Display KYC statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to include in statistics (default: 30)',
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Overall statistics
        total_records = KYCRecord.objects.count()
        recent_records = KYCRecord.objects.filter(created_at__gte=cutoff_date).count()
        
        # Status breakdown
        status_stats = KYCRecord.objects.values('status').annotate(count=Count('status'))
        
        # Recent status breakdown
        recent_status_stats = KYCRecord.objects.filter(
            created_at__gte=cutoff_date
        ).values('status').annotate(count=Count('status'))
        
        self.stdout.write(self.style.SUCCESS('=== KYC Statistics ==='))
        self.stdout.write(f'Total KYC Records: {total_records}')
        self.stdout.write(f'Records in last {days} days: {recent_records}')
        
        self.stdout.write('\n=== Overall Status Breakdown ===')
        for stat in status_stats:
            self.stdout.write(f'{stat["status"]}: {stat["count"]}')
        
        self.stdout.write(f'\n=== Last {days} Days Status Breakdown ===')
        for stat in recent_status_stats:
            self.stdout.write(f'{stat["status"]}: {stat["count"]}')
        
        # Approval rate
        approved = KYCRecord.objects.filter(status=KYCRecord.Status.APPROVED).count()
        rejected = KYCRecord.objects.filter(status=KYCRecord.Status.REJECTED).count()
        
        if approved + rejected > 0:
            approval_rate = (approved / (approved + rejected)) * 100
            self.stdout.write(f'\nApproval Rate: {approval_rate:.1f}%')

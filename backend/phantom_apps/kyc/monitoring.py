import logging
import time
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import KYCRecord, KYCEvent
import json

logger = logging.getLogger(__name__)

class KYCMonitoring:
    """
    Monitoring and metrics collection for KYC processes
    """
    
    def __init__(self):
        self.metrics = {}
    
    def collect_daily_metrics(self):
        """Collect daily KYC metrics"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Basic counts
        total_records = KYCRecord.objects.count()
        daily_submissions = KYCRecord.objects.filter(created_at__date=yesterday).count()
        pending_records = KYCRecord.objects.filter(status=KYCRecord.Status.PENDING).count()
        in_progress_records = KYCRecord.objects.filter(status=KYCRecord.Status.IN_PROGRESS).count()
        
        # Approval metrics
        approved_count = KYCRecord.objects.filter(
            status=KYCRecord.Status.APPROVED, 
            verified_at__date=yesterday
        ).count()
        
        rejected_count = KYCRecord.objects.filter(
            status=KYCRecord.Status.REJECTED,
            updated_at__date=yesterday
        ).count()
        
        # Calculate approval rate
        total_decisions = approved_count + rejected_count
        approval_rate = (approved_count / total_decisions * 100) if total_decisions > 0 else 0
        
        # Average processing time
        avg_processing_time = self.calculate_average_processing_time(yesterday)
        
        # Geographic distribution
        country_stats = KYCRecord.objects.values('country').annotate(count=Count('country')).order_by('-count')[:10]
        
        # Risk score distribution
        risk_stats = self.calculate_risk_distribution()
        
        self.metrics = {
            'date': yesterday.isoformat(),
            'total_records': total_records,
            'daily_submissions': daily_submissions,
            'pending_records': pending_records,
            'in_progress_records': in_progress_records,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'approval_rate': round(approval_rate, 2),
            'avg_processing_time_minutes': avg_processing_time,
            'country_distribution': list(country_stats),
            'risk_distribution': risk_stats,
            'timestamp': timezone.now().isoformat()
        }
        
        return self.metrics
    
    def calculate_average_processing_time(self, date):
        """Calculate average processing time for completed KYCs"""
        completed_records = KYCRecord.objects.filter(
            Q(status=KYCRecord.Status.APPROVED) | Q(status=KYCRecord.Status.REJECTED),
            updated_at__date=date
        ).exclude(verified_at__isnull=True)
        
        if not completed_records.exists():
            return 0
        
        total_minutes = 0
        count = 0
        
        for record in completed_records:
            if record.verified_at:
                processing_time = record.verified_at - record.created_at
                total_minutes += processing_time.total_seconds() / 60
                count += 1
        
        return round(total_minutes / count, 2) if count > 0 else 0
    
    def calculate_risk_distribution(self):
        """Calculate risk score distribution"""
        risk_ranges = [
            ('low', 0, 30),
            ('medium', 31, 70),
            ('high', 71, 100)
        ]
        
        distribution = {}
        for range_name, min_score, max_score in risk_ranges:
            count = KYCRecord.objects.filter(
                risk_score__gte=min_score,
                risk_score__lte=max_score
            ).count()
            distribution[range_name] = count
        
        return distribution
    
    def check_system_health(self):
        """Check KYC system health indicators"""
        health_status = {
            'status': 'healthy',
            'issues': [],
            'warnings': []
        }
        
        # Check for stuck records
        stuck_threshold = timezone.now() - timedelta(hours=2)
        stuck_records = KYCRecord.objects.filter(
            status=KYCRecord.Status.IN_PROGRESS,
            updated_at__lt=stuck_threshold
        ).count()
        
        if stuck_records > 0:
            health_status['warnings'].append(f"{stuck_records} records stuck in progress for >2 hours")
        
        # Check for high pending volume
        pending_count = KYCRecord.objects.filter(status=KYCRecord.Status.PENDING).count()
        if pending_count > 100:
            health_status['warnings'].append(f"High pending volume: {pending_count} records")
        
        # Check for low approval rate
        recent_records = KYCRecord.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=1)
        )
        
        if recent_records.exists():
            recent_approved = recent_records.filter(status=KYCRecord.Status.APPROVED).count()
            recent_rejected = recent_records.filter(status=KYCRecord.Status.REJECTED).count()
            total_recent = recent_approved + recent_rejected
            
            if total_recent > 10:  # Only check if we have enough data
                approval_rate = (recent_approved / total_recent) * 100
                if approval_rate < 50:  # Below 50% approval rate
                    health_status['issues'].append(f"Low approval rate: {approval_rate:.1f}%")
                    health_status['status'] = 'degraded'
        
        return health_status
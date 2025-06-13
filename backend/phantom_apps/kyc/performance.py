from django.core.cache import cache
from django.db import connection
from django.db.models import Prefetch
from .models import KYCRecord, KYCEvent
import time

class KYCPerformanceOptimizer:
    """Performance optimization utilities for KYC operations"""
    
    @staticmethod
    def get_kyc_with_events(user_id):
        """Optimized query to get KYC record with events"""
        cache_key = f"kyc_record_events_{user_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            kyc_record = KYCRecord.objects.select_related('user', 'reviewed_by').prefetch_related(
                Prefetch('events', queryset=KYCEvent.objects.order_by('-created_at')[:10])
            ).get(user_id=user_id)
            
            # Cache for 5 minutes for approved records, 1 minute for others
            cache_timeout = 300 if kyc_record.status == KYCRecord.Status.APPROVED else 60
            cache.set(cache_key, kyc_record, cache_timeout)
            
            return kyc_record
        except KYCRecord.DoesNotExist:
            return None
    
    @staticmethod
    def bulk_update_kyc_status(kyc_ids, status, batch_size=100):
        """Bulk update KYC statuses for performance"""
        updated_count = 0
        
        for i in range(0, len(kyc_ids), batch_size):
            batch = kyc_ids[i:i + batch_size]
            updated = KYCRecord.objects.filter(id__in=batch).update(
                status=status,
                updated_at=timezone.now()
            )
            updated_count += updated
        
        return updated_count
    
    @staticmethod
    def cleanup_old_events(days_to_keep=90):
        """Clean up old KYC events to maintain performance"""
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Keep important events even if old
        important_events = [
            KYCEvent.EventType.APPROVED,
            KYCEvent.EventType.REJECTED,
            KYCEvent.EventType.SESSION_CREATED
        ]
        
        deleted_count = KYCEvent.objects.filter(
            created_at__lt=cutoff_date
        ).exclude(
            event_type__in=important_events
        ).delete()[0]
        
        return deleted_count
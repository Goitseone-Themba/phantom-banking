from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import KYCRecord, KYCEvent

@receiver(post_save, sender=KYCRecord)
def kyc_status_changed(sender, instance, created, **kwargs):
    """
    Signal handler for KYC status changes
    """
    if created:
        # Create initial event
        KYCEvent.objects.create(
            kyc_record=instance,
            event_type=KYCEvent.EventType.SESSION_CREATED,
            description=f"KYC record created for {instance.user.username}",
            metadata={'initial_status': instance.status}
        )
    else:
        # Check if status changed
        if hasattr(instance, '_state') and instance._state.adding is False:
            try:
                old_instance = KYCRecord.objects.get(pk=instance.pk)
                if old_instance.status != instance.status:
                    event_type = KYCEvent.EventType.VERIFICATION_COMPLETED
                    if instance.status == KYCRecord.Status.APPROVED:
                        event_type = KYCEvent.EventType.APPROVED
                    elif instance.status == KYCRecord.Status.REJECTED:
                        event_type = KYCEvent.EventType.REJECTED
                    
                    KYCEvent.objects.create(
                        kyc_record=instance,
                        event_type=event_type,
                        description=f"Status changed from {old_instance.status} to {instance.status}",
                        metadata={
                            'old_status': old_instance.status,
                            'new_status': instance.status
                        }
                    )
            except KYCRecord.DoesNotExist:
                pass
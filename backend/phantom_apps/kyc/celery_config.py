from celery.schedules import crontab

beat_schedule = {
    'check-kyc-status-every-5-minutes': {
        'task': 'phantom_apps.kyc.tasks.check_kyc_status_periodic',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-expired-kyc-daily': {
        'task': 'phantom_apps.kyc.tasks.cleanup_expired_kyc_sessions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'generate-kyc-report-daily': {
        'task': 'phantom_apps.kyc.tasks.generate_kyc_report',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
}



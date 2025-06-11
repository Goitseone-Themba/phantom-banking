# KYC Integration Guide for Phantom Banking System

## 1. File Structure

Add these files to your existing project structure:

```
backend/
├── phantom_apps/
│   ├── kyc/                          # New KYC app
│   │   ├── __init__.py
│   │   ├── admin.py                  # Admin interface
│   │   ├── apps.py                   # App configuration
│   │   ├── models.py                 # KYC models
│   │   ├── serializers.py            # DRF serializers
│   │   ├── views.py                  # API views
│   │   ├── urls.py                   # URL patterns
│   │   ├── signals.py                # Django signals
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py       # Initial migration
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── veriff_service.py     # Veriff API integration
│   │   │   └── wallet_service.py     # Wallet upgrade logic
│   │   └── management/
│   │       ├── __init__.py
│   │       └── commands/
│   │           ├── __init__.py
│   │           └── check_kyc_status.py
```

## 2. Dependencies

Add these to your `requirements.txt`:

```txt
# KYC Dependencies
requests>=2.31.0
cryptography>=41.0.0
```

## 3. Django Settings

Add to your `settings.py`:

```python
# Add KYC app to INSTALLED_APPS
INSTALLED_APPS = [
    # ... your existing apps
    'phantom_apps.kyc',
]

# Veriff Configuration
VERIFF_API_KEY = os.getenv('VERIFF_API_KEY', '')
VERIFF_API_SECRET = os.getenv('VERIFF_API_SECRET', '')
VERIFF_BASE_URL = os.getenv('VERIFF_BASE_URL', 'https://stationapi.veriff.com')  # Use sandbox for testing
VERIFF_WEBHOOK_SECRET = os.getenv('VERIFF_WEBHOOK_SECRET', '')

# Frontend URL for callbacks
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'kyc.log',
        },
    },
    'loggers': {
        'phantom_apps.kyc': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 4. Environment Variables

Add to your `.env` file:

```env
# Veriff KYC Configuration
VERIFF_API_KEY=your_veriff_api_key
VERIFF_API_SECRET=your_veriff_api_secret
VERIFF_BASE_URL=https://stationapi.veriff.com
VERIFF_WEBHOOK_SECRET=your_webhook_secret
FRONTEND_URL=http://localhost:3000
```

## 5. URL Configuration

Update your main `urls.py`:

```python
# backend/phantom_banking_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... your existing URLs
    path('', include('phantom_apps.kyc.urls')),  # Add KYC URLs
]
```

## 6. Database Migration

Run these commands to set up the database:

```bash
# Create and apply migrations
python manage.py makemigrations kyc
python manage.py migrate

# Create superuser if you haven't already
python manage.py createsuperuser
```

## 7. Integration with Existing Wallet System

Update your existing wallet model to include KYC-related fields:

```python
# In your existing wallets/models.py
class Wallet(models.Model):
    # ... existing fields
    
    # Add these KYC-related fields
    is_kyc_verified = models.BooleanField(default=False)
    wallet_type = models.CharField(max_length=20, default='basic')  # basic, verified, premium
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2, default=100000)
    upgraded_at = models.DateTimeField(null=True, blank=True)
```

## 8. Testing the Integration

### 8.1 Create a test user and start KYC:

```python
# Test script or Django shell
from django.contrib.auth.models import User
from phantom_apps.kyc.models import KYCRecord
from phantom_apps.kyc.services.veriff_service import VeriffService

# Create test user
user = User.objects.create_user('testuser', 'test@example.com', 'password')

# Start KYC process
kyc_data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'date_of_birth': '1990-01-01',
    'nationality': 'BW',
    'document_type': 'passport',
    'document_number': 'BP123456789',
    'address_line_1': '123 Main St',
    'city': 'Gaborone',
    'state_province': 'South East',
    'postal_code': '00000',
    'country': 'BW'
}

kyc_record = KYCRecord.objects.create(user=user, **kyc_data)
veriff_service = VeriffService()
success, result = veriff_service.create_verification_session(kyc_record)
print(f"Session created: {success}")
print(f"Session URL: {result.get('session_url')}")
```

### 8.2 API Endpoints to test:

```bash
# Get KYC summary
GET /api/kyc/summary/

# Start verification
POST /api/kyc/records/start_verification/
{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "nationality": "BW",
    "document_type": "passport",
    "document_number": "BP123456789",
    "address_line_1": "123 Main St",
    "city": "Gaborone",
    "state_province": "South East",
    "postal_code": "00000",
    "country": "BW"
}

# Check KYC status
GET /api/kyc/records/{id}/status/

# Get KYC events
GET /api/kyc/records/{id}/events/

# Webhook endpoint (for Veriff)
POST /api/kyc/webhook/veriff/
```

## 9. Frontend Integration Examples

### React Component Example:

```jsx
// KYCVerification.jsx
import React, { useState } from 'react';
import axios from 'axios';

const KYCVerification = () => {
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        date_of_birth: '',
        nationality: 'BW',
        document_type: 'passport',
        document_number: '',
        address_line_1: '',
        city: '',
        state_province: '',
        postal_code: '',
        country: 'BW'
    });
    const [loading, setLoading] = useState(false);
    const [sessionUrl, setSessionUrl] = useState(null);

    const startKYC = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/kyc/records/start_verification/', formData);
            setSessionUrl(response.data.session_url);
        } catch (error) {
            console.error('KYC start failed:', error);
        }
        setLoading(false);
    };

    if (sessionUrl) {
        // Redirect to Veriff session
        window.location.href = sessionUrl;
        return <div>Redirecting to verification...</div>;
    }

    return (
        <form onSubmit={(e) => { e.preventDefault(); startKYC(); }}>
            {/* Your form fields here */}
            <button type="submit" disabled={loading}>
                {loading ? 'Starting Verification...' : 'Start KYC Verification'}
            </button>
        </form>
    );
};
```

## 10. Veriff Webhook Setup

In your production environment, configure Veriff webhook URL:
`https://yourdomain.com/api/kyc/webhook/veriff/`

## 11. Admin Interface

Access the Django admin at `/admin/` to:
- View all KYC records
- Manually approve/reject verifications
- View KYC events and documents
- Monitor verification status

## 12. Monitoring and Logging

Monitor KYC activities:

```bash
# View KYC logs
tail -f kyc.log

# Check KYC status via management command
python manage.py check_kyc_status
```

## 13. Security Considerations

1. **Webhook Security**: Always verify webhook signatures
2. **Data Protection**: Encrypt sensitive KYC data at rest
3. **Access Control**: Restrict admin access to KYC data
4. **Audit Trail**: All KYC events are logged automatically
5. **GDPR Compliance**: Implement data retention policies

## 14. Production Deployment

1. Set up proper SSL certificates
2. Configure production Veriff API keys
3. Set up monitoring and alerting
4. Implement backup strategies for KYC data
5. Configure load balancing for webhook endpoints

## 15. Testing Checklist

- [ ] KYC record creation
- [ ] Veriff session creation
- [ ] Webhook processing
- [ ] Wallet upgrade after approval
- [ ] Admin interface functionality
- [ ] API endpoint responses
- [ ] Error handling
- [ ] Logging functionality



# Database optimization queries
DATABASE_OPTIMIZATIONS = """
-- Add these indexes to your PostgreSQL database for better performance

-- KYC Records indexes
CREATE INDEX CONCURRENTLY idx_kyc_records_status ON kyc_records(status);
CREATE INDEX CONCURRENTLY idx_kyc_records_user_status ON kyc_records(user_id, status);
CREATE INDEX CONCURRENTLY idx_kyc_records_created_at ON kyc_records(created_at);
CREATE INDEX CONCURRENTLY idx_kyc_records_veriff_session ON kyc_records(veriff_session_id);
CREATE INDEX CONCURRENTLY idx_kyc_records_country_created ON kyc_records(country, created_at);

-- KYC Events indexes
CREATE INDEX CONCURRENTLY idx_kyc_events_record_type ON kyc_events(kyc_record_id, event_type);
CREATE INDEX CONCURRENTLY idx_kyc_events_created_at ON kyc_events(created_at);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_kyc_status_updated ON kyc_records(status, updated_at);
CREATE INDEX CONCURRENTLY idx_kyc_verification_level ON kyc_records(verification_level, status);

-- Partial indexes for active records
CREATE INDEX CONCURRENTLY idx_kyc_active_records ON kyc_records(created_at) 
WHERE status IN ('pending', 'in_progress');
"""

# Monitoring queries
MONITORING_QUERIES = """
-- KYC Performance Monitoring Queries

-- Check for slow KYC processes
SELECT 
    id, 
    user_id, 
    status, 
    created_at, 
    updated_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_since_created
FROM kyc_records 
WHERE status IN ('pending', 'in_progress') 
    AND created_at < NOW() - INTERVAL '1 hour'
ORDER BY created_at;

-- Daily KYC statistics
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_submissions,
    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
    ROUND(AVG(CASE WHEN verified_at IS NOT NULL THEN 
        EXTRACT(EPOCH FROM (verified_at - created_at))/60 
    END), 2) as avg_processing_minutes
FROM kyc_records 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Country-wise KYC distribution
SELECT 
    country,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
    ROUND(COUNT(CASE WHEN status = 'approved' THEN 1 END) * 100.0 / COUNT(*), 2) as approval_rate
FROM kyc_records 
GROUP BY country 
ORDER BY total DESC;

-- Check for potential fraud patterns
SELECT 
    document_number,
    COUNT(*) as usage_count,
    STRING_AGG(DISTINCT user_id::text, ', ') as user_ids
FROM kyc_records 
GROUP BY document_number 
HAVING COUNT(*) > 1;
"""

# Logging configuration
LOGGING_CONFIG = """
# Add this to your Django settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'kyc_formatter': {
            'format': '[KYC] {levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'kyc_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/kyc.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 5,
            'formatter': 'kyc_formatter',
        },
        'kyc_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/kyc_security.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'phantom_apps.kyc': {
            'handlers': ['kyc_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'phantom_apps.kyc.security': {
            'handlers': ['kyc_security', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'phantom_apps.kyc.services': {
            'handlers': ['kyc_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
"""

# Environment-specific settings
ENVIRONMENT_SETTINGS = '''
# Production settings for KYC

# security.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# KYC specific security settings
KYC_SESSION_TIMEOUT = 3600  # 1 hour
KYC_MAX_RETRIES = 3
KYC_RATE_LIMIT_PER_IP = 5  # per hour
KYC_WEBHOOK_TIMEOUT = 30  # seconds

# Caching settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'kyc',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Celery settings for KYC
CELERY_BEAT_SCHEDULE = {
    'check-kyc-status': {
        'task': 'phantom_apps.kyc.tasks.check_kyc_status_periodic',
        'schedule': crontab(minute='*/5'),
    },
    'cleanup-expired-sessions': {
        'task': 'phantom_apps.kyc.tasks.cleanup_expired_kyc_sessions',
        'schedule': crontab(hour=2, minute=0),
    },
    'generate-daily-report': {
        'task': 'phantom_apps.kyc.tasks.generate_kyc_report',
        'schedule': crontab(hour=8, minute=0),
    },
}

# Monitoring and alerting
KYC_ALERT_THRESHOLDS = {
    'pending_records_limit': 100,
    'approval_rate_minimum': 50,  # percentage
    'processing_time_maximum': 120,  # minutes
    'stuck_records_threshold': 2,  # hours
}
'''



# BPMN Workflow Documentation
BPMN_WORKFLOW = """
# BPMN Workflow for KYC Verification Process

## Workflow 1: Customer KYC Verification

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" 
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                 id="KYC_Verification_Process">
  
  <bpmn:process id="kyc_verification" name="KYC Verification Process" isExecutable="true">
    
    <!-- Start Event -->
    <bpmn:startEvent id="start_kyc" name="Customer Initiates KYC">
      <bpmn:outgoing>flow_to_data_collection</bpmn:outgoing>
    </bpmn:startEvent>
    
    <!-- User Task: Data Collection -->
    <bpmn:userTask id="collect_user_data" name="Collect Personal Information">
      <bpmn:incoming>flow_to_data_collection</bpmn:incoming>
      <bpmn:outgoing>flow_to_validation</bpmn:outgoing>
      <bpmn:documentation>
        Customer provides:
        - Personal information (name, DOB, nationality)
        - Document information (type, number)
        - Address information
      </bpmn:documentation>
    </bpmn:userTask>
    
    <!-- Service Task: Data Validation -->
    <bpmn:serviceTask id="validate_data" name="Validate Input Data">
      <bpmn:incoming>flow_to_validation</bpmn:incoming>
      <bpmn:outgoing>flow_to_gateway_validation</bpmn:outgoing>
      <bpmn:documentation>
        System validates:
        - Required fields present
        - Age requirements (18+)
        - Document number format
        - Address format
      </bpmn:documentation>
    </bpmn:serviceTask>
    
    <!-- Exclusive Gateway: Validation Check -->
    <bpmn:exclusiveGateway id="gateway_validation" name="Data Valid?">
      <bpmn:incoming>flow_to_gateway_validation</bpmn:incoming>
      <bpmn:outgoing>flow_validation_success</bpmn:outgoing>
      <bpmn:outgoing>flow_validation_failure</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    
    <!-- Service Task: Create Veriff Session -->
    <bpmn:serviceTask id="create_veriff_session" name="Create Veriff Verification Session">
      <bpmn:incoming>flow_validation_success</bpmn:incoming>
      <bpmn:outgoing>flow_to_document_upload</bpmn:outgoing>
      <bpmn:documentation>
        - Create KYC record in database
        - Call Veriff API to create session
        - Generate session URL for user
      </bpmn:documentation>
    </bpmn:serviceTask>
    
    <!-- User Task: Document Upload -->
    <bpmn:userTask id="upload_documents" name="Upload Identity Documents">
      <bpmn:incoming>flow_to_document_upload</bpmn:incoming>
      <bpmn:outgoing>flow_to_verification</bpmn:outgoing>
      <bpmn:documentation>
        Customer uploads:
        - Government ID (front and back)
        - Selfie photo
        - Additional documents if required
      </bpmn:documentation>
    </bpmn:userTask>
    
    <!-- Service Task: Automatic Verification -->
    <bpmn:serviceTask id="auto_verification" name="Automated Verification Process">
      <bpmn:incoming>flow_to_verification</bpmn:incoming>
      <bpmn:outgoing>flow_to_gateway_verification</bpmn:outgoing>
      <bpmn:documentation>
        Veriff performs:
        - Document authenticity check
        - Face matching
        - Data extraction and validation
        - Risk assessment
      </bpmn:documentation>
    </bpmn:serviceTask>
    
    <!-- Exclusive Gateway: Verification Result -->
    <bpmn:exclusiveGateway id="gateway_verification" name="Verification Result">
      <bpmn:incoming>flow_to_gateway_verification</bpmn:incoming>
      <bpmn:outgoing>flow_approved</bpmn:outgoing>
      <bpmn:outgoing>flow_rejected</bpmn:outgoing>
      <bpmn:outgoing>flow_resubmission</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    
    <!-- Service Task: Approve KYC -->
    <bpmn:serviceTask id="approve_kyc" name="Approve KYC">
      <bpmn:incoming>flow_approved</bpmn:incoming>
      <bpmn:outgoing>flow_to_wallet_upgrade</bpmn:outgoing>
      <bpmn:documentation>
        - Update KYC status to approved
        - Set verification timestamp
        - Log approval event
        - Send approval notification
      </bpmn:documentation>
    </bpmn:serviceTask>
    
    <!-- Service Task: Wallet Upgrade -->
    <bpmn:serviceTask id="upgrade_wallet" name="Upgrade User Wallet">
      <bpmn:incoming>flow_to_wallet_upgrade</bpmn:incoming>
      <bpmn:outgoing>flow_to_success_end</bpmn:outgoing>
      <bpmn:documentation>
        - Upgrade wallet type to verified
        - Increase transaction limits
        - Enable premium features
        - Send upgrade notification
      </bpmn:documentation>
    </bpmn:serviceTask>
    
    <!-- Service Task: Reject KYC -->
    <bpmn:serviceTask id="reject_kyc" name="Reject KYC">
      <bpmn:incoming>flow_rejected</bpmn:incoming>
      <bpmn:outgoing>flow_to_rejection_end</bpmn:outgoing>
      <bpmn:documentation>
        - Update KYC status to rejected
        - Log rejection reason
        - Send rejection notification
        - Provide guidance for resubmission
      </bpmn:documentation>
    </bpmn:serviceTask>
    
    <!-- Service Task: Request Resubmission -->
    <bpmn:serviceTask id="request_resubmission" name="Request Document Resubmission">
      <bpmn:incoming>flow_resubmission</bpmn:incoming>
      <bpmn:outgoing>flow_to_resubmission_end</bpmn:outgoing>
      <bpmn:documentation>
        - Update status to resubmission required
        - Send resubmission notification
        - Provide specific guidance
        - Allow user to restart process
      </bpmn:documentation>
    </bpmn:serviceTask>
    
    <!-- End Events -->
    <bpmn:endEvent id="end_success" name="KYC Approved">
      <bpmn:incoming>flow_to_success_end</bpmn:incoming>
    </bpmn:endEvent>
    
    <bpmn:endEvent id="end_rejection" name="KYC Rejected">
      <bpmn:incoming>flow_to_rejection_end</bpmn:incoming>
    </bpmn:endEvent>
    
    <bpmn:endEvent id="end_resubmission" name="Resubmission Required">
      <bpmn:incoming>flow_to_resubmission_end</bpmn:incoming>
    </bpmn:endEvent>
    
    <bpmn:endEvent id="end_validation_failure" name="Validation Failed">
      <bpmn:incoming>flow_validation_failure</bpmn:incoming>
    </bpmn:endEvent>
    
    <!-- Sequence Flows -->
    <bpmn:sequenceFlow id="flow_to_data_collection" sourceRef="start_kyc" targetRef="collect_user_data"/>
    <bpmn:sequenceFlow id="flow_to_validation" sourceRef="collect_user_data" targetRef="validate_data"/>
    <bpmn:sequenceFlow id="flow_to_gateway_validation" sourceRef="validate_data" targetRef="gateway_validation"/>
    <bpmn:sequenceFlow id="flow_validation_success" sourceRef="gateway_validation" targetRef="create_veriff_session">
      <bpmn:conditionExpression>#{validation_result == 'success'}</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="flow_validation_failure" sourceRef="gateway_validation" targetRef="end_validation_failure">
      <bpmn:conditionExpression>#{validation_result == 'failure'}</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="flow_to_document_upload" sourceRef="create_veriff_session" targetRef="upload_documents"/>
    <bpmn:sequenceFlow id="flow_to_verification" sourceRef="upload_documents" targetRef="auto_verification"/>
    <bpmn:sequenceFlow id="flow_to_gateway_verification" sourceRef="auto_verification" targetRef="gateway_verification"/>
    <bpmn:sequenceFlow id="flow_approved" sourceRef="gateway_verification" targetRef="approve_kyc">
      <bpmn:conditionExpression>#{verification_decision == 'approved'}</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="flow_rejected" sourceRef="gateway_verification" targetRef="reject_kyc">
      <bpmn:conditionExpression>#{verification_decision == 'declined'}</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="flow_resubmission" sourceRef="gateway_verification" targetRef="request_resubmission">
      <bpmn:conditionExpression>#{verification_decision == 'resubmission_requested'}</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="flow_to_wallet_upgrade" sourceRef="approve_kyc" targetRef="upgrade_wallet"/>
    <bpmn:sequenceFlow id="flow_to_success_end" sourceRef="upgrade_wallet" targetRef="end_success"/>
    <bpmn:sequenceFlow id="flow_to_rejection_end" sourceRef="reject_kyc" targetRef="end_rejection"/>
    <bpmn:sequenceFlow id="flow_to_resubmission_end" sourceRef="request_resubmission" targetRef="end_resubmission"/>
    
  </bpmn:process>
</bpmn:definitions>
```

## Workflow 2: Admin Review Process (Optional Manual Review)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" 
                 id="KYC_Admin_Review">
  
  <bpmn:process id="kyc_admin_review" name="KYC Admin Review Process" isExecutable="true">
    
    <bpmn:startEvent id="start_admin_review" name="Manual Review Required">
      <bpmn:outgoing>flow_to_assignment</bpmn:outgoing>
    </bpmn:startEvent>
    
    <bpmn:serviceTask id="assign_reviewer" name="Assign to Reviewer">
      <bpmn:incoming>flow_to_assignment</bpmn:incoming>
      <bpmn:outgoing>flow_to_review</bpmn:outgoing>
    </bpmn:serviceTask>
    
    <bpmn:userTask id="manual_review" name="Manual Document Review">
      <bpmn:incoming>flow_to_review</bpmn:incoming>
      <bpmn:outgoing>flow_to_decision</bpmn:outgoing>
      <bpmn:documentation>
        Admin reviewer checks:
        - Document quality and authenticity
        - Data consistency
        - Risk factors
        - Compliance requirements
      </bpmn:documentation>
    </bpmn:userTask>
    
    <bpmn:exclusiveGateway id="admin_decision" name="Admin Decision">
      <bpmn:incoming>flow_to_decision</bpmn:incoming>
      <bpmn:outgoing>flow_admin_approve</bpmn:outgoing>
      <bpmn:outgoing>flow_admin_reject</bpmn:outgoing>
      <bpmn:outgoing>flow_admin_escalate</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    
    <bpmn:serviceTask id="admin_approve" name="Admin Approval">
      <bpmn:incoming>flow_admin_approve</bpmn:incoming>
      <bpmn:outgoing>flow_to_approved_end</bpmn:outgoing>
    </bpmn:serviceTask>
    
    <bpmn:serviceTask id="admin_reject" name="Admin Rejection">
      <bpmn:incoming>flow_admin_reject</bpmn:incoming>
      <bpmn:outgoing>flow_to_rejected_end</bpmn:outgoing>
    </bpmn:serviceTask>
    
    <bpmn:userTask id="escalate_review" name="Escalate to Senior Reviewer">
      <bpmn:incoming>flow_admin_escalate</bpmn:incoming>
      <bpmn:outgoing>flow_to_escalation_end</bpmn:outgoing>
    </bpmn:userTask>
    
    <bpmn:endEvent id="end_approved" name="Admin Approved"/>
    <bpmn:endEvent id="end_rejected" name="Admin Rejected"/>
    <bpmn:endEvent id="end_escalated" name="Escalated"/>
    
  </bpmn:process>
</bpmn:definitions>
```

## Process Variables and Data Objects

### KYC Process Variables:
- `customer_id`: User identifier
- `kyc_record_id`: KYC record UUID
- `veriff_session_id`: Veriff session identifier
- `validation_result`: Data validation result (success/failure)
- `verification_decision`: Veriff decision (approved/declined/resubmission_requested)
- `risk_score`: Calculated risk score
- `admin_review_required`: Boolean flag for manual review
- `reviewer_id`: Assigned reviewer identifier

### Process Execution Rules:
1. **Automatic Processing**: Most KYC verifications are processed automatically
2. **Manual Review Triggers**: 
   - High risk score (>80)
   - Inconsistent data
   - Document quality issues
   - Fraud indicators
3. **SLA Targets**:
   - Automatic verification: < 5 minutes
   - Manual review: < 24 hours
   - Escalated review: < 48 hours
"""

# Postman Collection Export
POSTMAN_COLLECTION = '''
{
  "info": {
    "name": "Phantom Banking KYC API",
    "description": "API collection for KYC verification endpoints",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\\"username\\": \\"testuser\\", \\"password\\": \\"testpass123\\"}"
            },
            "url": {
              "raw": "{{base_url}}/api/auth/login/",
              "host": ["{{base_url}}"],
              "path": ["api", "auth", "login", ""]
            }
          }
        }
      ]
    },
    {
      "name": "KYC",
      "item": [
        {
          "name": "Get KYC Summary",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/api/kyc/summary/",
              "host": ["{{base_url}}"],
              "path": ["api", "kyc", "summary", ""]
            }
          }
        },
        {
          "name": "Start KYC Verification",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\\"first_name\\": \\"John\\", \\"last_name\\": \\"Doe\\", \\"date_of_birth\\": \\"1990-01-01\\", \\"nationality\\": \\"BW\\", \\"document_type\\": \\"passport\\", \\"document_number\\": \\"BP123456789\\", \\"address_line_1\\": \\"123 Main St\\", \\"city\\": \\"Gaborone\\", \\"state_province\\": \\"South East\\", \\"postal_code\\": \\"00000\\", \\"country\\": \\"BW\\"}"
            },
            "url": {
              "raw": "{{base_url}}/api/kyc/records/start_verification/",
              "host": ["{{base_url}}"],
              "path": ["api", "kyc", "records", "start_verification", ""]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "access_token",
      "value": "your_jwt_token_here"
    }
  ]
}
'''

CELERY_BEAT_SCHEDULE = """
##Add this to your main celery.py file

This integration provides a complete KYC solution that seamlessly integrates with your existing Phantom Banking System while maintaining security and compliance standards.
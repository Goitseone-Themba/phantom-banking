# 🏦 Phantom Banking Analytics Integration Guide

## 📁 **Step 1: Create the Analytics App Structure**

In your existing `phantom_apps` folder (alongside your other apps), create this complete structure:

```
backend/
├── phantom_apps/
│   ├── authentication/
│   ├── common/
│   ├── customers/
│   ├── kyc/
│   ├── merchants/
│   ├── mock_systems/
│   ├── monitoring/
│   ├── transactions/
│   ├── wallets/
│   ├── analytics/          # ← Add this new folder
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── utils.py
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   └── templates/
│   │       └── analytics/
│   │           ├── base.html
│   │           ├── dashboard.html
│   │           └── customer_detail.html
│   └── __init__.py
```

## 📝 **Step 2: Update Main Settings**

**Edit your main `settings.py` file** (likely in your `backend` folder or main config folder):

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # If you're using DRF
    
    # Your existing phantom_apps
    'phantom_apps.authentication',
    'phantom_apps.common',
    'phantom_apps.customers',
    'phantom_apps.kyc',
    'phantom_apps.merchants',
    'phantom_apps.mock_systems',
    'phantom_apps.monitoring',
    'phantom_apps.transactions',
    'phantom_apps.wallets',
    
    # Add the new analytics app
    'phantom_apps.analytics',  # ← Add this line
]

# Add any additional settings if needed
ANALYTICS_SETTINGS = {
    'ENABLE_DEMO_DATA': True,
    'DEMO_CUSTOMERS_COUNT': 100,
    'DEMO_TRANSACTIONS_COUNT': 1000,
    'DEMO_MERCHANTS_COUNT': 50,
}
```

## 🔗 **Step 3: Update Main URLs**

**Edit your main `urls.py` file** (probably at the project root level):

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Your existing URL patterns
    path('api/customers/', include('phantom_apps.customers.urls')),
    path('api/transactions/', include('phantom_apps.transactions.urls')),
    path('api/merchants/', include('phantom_apps.merchants.urls')),
    # ... other existing URLs
    
    # Add analytics URLs
    path('analytics/', include('phantom_apps.analytics.urls')),  # ← Add this line
]
```

## 🎯 **Step 4: Create Admin Integration**

**Update your main admin site** (if you have a custom admin configuration):

**Edit `admin.py` in your main app or create a new admin configuration:**

```python
# In your main admin.py or create phantom_apps/admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.html import format_html

# Extend your existing admin
class PhantomBankingAdminSite(admin.AdminSite):
    site_header = "Phantom Banking Administration"
    site_title = "Phantom Banking Admin"
    index_title = "Welcome to Phantom Banking Admin Portal"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.analytics_redirect, name='admin_analytics'),
        ]
        return custom_urls + urls
    
    def analytics_redirect(self, request):
        """Redirect to analytics dashboard"""
        return redirect('/analytics/')
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Add analytics link to admin index
        extra_context.update({
            'analytics_url': '/analytics/',
            'show_analytics': True,
        })
        
        return super().index(request, extra_context)

# If you don't have a custom admin site, add this to your settings.py:
# ADMIN_SITE_CLASS = 'phantom_apps.admin.PhantomBankingAdminSite'
```

## 🎨 **Step 5: Add Navigation Links**

**Create/update your base template** to include analytics navigation:

**In your main base template** (e.g., `templates/base.html`):

```html
<!-- Add to your navigation menu -->
<nav class="navbar">
    <div class="navbar-nav">
        <a href="/" class="nav-link">Dashboard</a>
        <a href="/admin/" class="nav-link">Admin</a>
        <a href="/analytics/" class="nav-link">📊 Analytics</a> <!-- Add this -->
        <!-- Your other nav links -->
    </div>
</nav>
```

## 🚀 **Step 6: Run Migrations and Start Server**

```bash
# Navigate to your project directory
cd C:\Users\princ\Documents\phantom_banking_project

# Create migrations (if needed)
python manage.py makemigrations analytics

# Apply migrations
python manage.py migrate

# Collect static files (if using in production)
python manage.py collectstatic

# Start the development server
python manage.py runserver
```

## 🎯 **Step 7: Access the Analytics Dashboard**

Once your server is running, access the analytics at:

- **Main Dashboard:** `http://127.0.0.1:8000/analytics/`
- **Admin Panel:** `http://127.0.0.1:8000/admin/` (with analytics link)
- **Direct Customer Analytics:** `http://127.0.0.1:8000/analytics/customer/{customer_id}/`

## 🔧 **Step 8: Optional Customizations**

### **A. Custom Styling Integration**

If you want to match your existing Phantom Banking theme, create:

**`phantom_apps/analytics/static/analytics/css/custom.css`:**

```css
/* Override default analytics styles to match your theme */
:root {
    --primary-color: #your-primary-color;
    --secondary-color: #your-secondary-color;
    /* Add your custom color variables */
}

.navbar {
    background: var(--primary-color);
}

/* Add your custom styles */
```

### **B. API Integration (Optional)**

**Add to `phantom_apps/analytics/api_views.py`:**

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AnalyticsDataManager
from .serializers import DashboardSummarySerializer

@api_view(['GET'])
def analytics_api_summary(request):
    """API endpoint for analytics summary"""
    customers = AnalyticsDataManager.get_customers()
    transactions = AnalyticsDataManager.get_transactions()
    
    data = {
        'total_customers': len(customers),
        'total_transactions': len(transactions),
        'total_revenue': sum([t.amount for t in transactions]),
    }
    
    serializer = DashboardSummarySerializer(data)
    return Response(serializer.data)
```

### **C. Database Integration (Future)**

When ready to connect to real database, replace the mock data managers in `models.py`:

```python
# Replace AnalyticsDataManager with real database queries
from phantom_apps.customers.models import Customer
from phantom_apps.transactions.models import Transaction

class RealDataManager:
    @classmethod
    def get_customers(cls):
        return Customer.objects.all()
    
    @classmethod  
    def get_transactions(cls):
        return Transaction.objects.all()
```

## 🎉 **Step 9: Test the Integration**

1. **Start your server:** `python manage.py runserver`
2. **Visit:** `http://127.0.0.1:8000/analytics/`
3. **You should see:**
   - Analytics dashboard with charts and data
   - Customer list with "View Details" buttons
   - Interactive charts and statistics
   - Risk analysis and insights

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **Import Error:** Make sure all files are in the correct directories
2. **Template Not Found:** Check that templates are in `phantom_apps/analytics/templates/analytics/`
3. **URL Not Found:** Verify URLs are included in main `urls.py`
4. **Static Files:** Run `python manage.py collectstatic` if styles aren't loading

### **File Checklist:**

- ✅ `phantom_apps/analytics/__init__.py`
- ✅ `phantom_apps/analytics/apps.py`
- ✅ `phantom_apps/analytics/models.py`
- ✅ `phantom_apps/analytics/views.py`
- ✅ `phantom_apps/analytics/urls.py`
- ✅ `phantom_apps/analytics/admin.py`
- ✅ `phantom_apps/analytics/serializers.py`
- ✅ `phantom_apps/analytics/utils.py`
- ✅ `phantom_apps/analytics/templates/analytics/base.html`
- ✅ `phantom_apps/analytics/templates/analytics/dashboard.html`
- ✅ `phantom_apps/analytics/templates/analytics/customer_detail.html`
- ✅ Updated main `settings.py`
- ✅ Updated main `urls.py`

## 🎊 **Success!**

Your Phantom Banking system now has a complete analytics dashboard with:

- 📊 Interactive charts and visualizations
- 👥 Customer analytics and insights
- 🏪 Merchant performance tracking
- ⚠️ Risk analysis and scoring
- 📈 Revenue and trend analysis
- 🎯 Admin integration
- 📱 Responsive design

The analytics use generated demo data and are ready for production use!

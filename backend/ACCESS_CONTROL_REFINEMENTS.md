# Access Control Refinements - Admin-Only Model

This document outlines the refined access control model where **only administrators** can grant, modify, or revoke merchant access to customer wallets.

## Key Principle: Admin-Only Access Control

**Merchants cannot restrict access to customer wallets** - only administrators have this authority.

## What Changed

### Before Refinement
- Merchants could potentially grant access to other merchants
- Wallet creators had special privileges over access control
- Access management was merchant-driven

### After Refinement
- **Only administrators** can grant, modify, or revoke wallet access
- Merchants can only create wallets (auto-grants them access)
- All other access changes must go through admin interface
- Clear separation between business operations and access control

## Access Control Flow

### 1. Wallet Creation (Automatic Access)
```
 Merchant creates wallet → Automatically gets FULL access
 No admin intervention needed for this step
```

### 2. Additional Access Requests (Admin Required)
```
 Merchant needs access to existing wallet
    ↓
 Request admin to grant access
    ↓
 Admin reviews and grants/denies through admin interface
    ↓
 Access granted with appropriate level (full/credit_only/view_only)
```

### 3. Access Modification (Admin Only)
```
 Need to change access level or revoke access
    ↓
 Admin uses admin interface
    ↓
 Changes applied with audit trail
```

## Admin Interface Features

### Access Management Dashboard
- **View all merchant-customer access relationships**
- **Grant new access** with reason tracking
- **Modify existing access levels**
- **Suspend or revoke access** with reason
- **Set expiration dates** for access
- **Audit trail** of all changes

### Admin Actions Available
1. **Suspend Access** - Temporarily disable merchant access
2. **Reactivate Access** - Restore suspended access
3. **Extend Access** - Add time to expiring access
4. **Change Access Level** - Modify permissions (full/credit_only/view_only)
5. **Revoke Access** - Permanently remove access

### Access Reasons Tracked
- `wallet_creation` - Automatic access for wallet creator
- `business_partnership` - Admin approved business partnership
- `customer_request` - Customer requested merchant access
- `admin_grant` - Manual admin approval
- `api_integration` - Technical integration approval

## Merchant Perspective

### What Merchants Can Do
✅ **Create wallets** for new customers (auto-grants full access)  
✅ **View wallets** they have access to  
✅ **Perform transactions** based on their access level  
✅ **See their transaction history** on accessible wallets  

### What Merchants Cannot Do
❌ **Grant access** to other merchants  
❌ **Revoke access** from other merchants  
❌ **Modify access levels** of any merchant  
❌ **Suspend** other merchants' access  
❌ **Set expiration dates** for access  

### When Merchants Need Admin Help
- Want access to existing customer wallet
- Need to change their access level
- Have disputes about wallet access
- Need access restored after suspension
- Require special permissions for partnerships

## API Behavior Changes

### Wallet Creation/Access Endpoint
```
POST /api/v1/wallets/create-or-access/
```
**New Behavior:**
- Creates wallet → Auto-grants full access
- Finds existing wallet → Returns current access level
- **No longer accepts `access_type` parameter**
- Returns clear message about admin-controlled access

### Response Messages
- **Wallet created:** "Wallet created successfully with automatic full access"
- **Existing wallet with access:** "Existing wallet found. You have [access_type] access"
- **Existing wallet no access:** "Wallet found but no access. Contact administrator for access."

## Security Benefits

### 1. Centralized Control
- All access decisions go through trained administrators
- Prevents merchants from making unauthorized access changes
- Clear accountability for access management

### 2. Audit Trail
- Every access change is logged with admin who made it
- Reasons for access grants/revocations are tracked
- Complete history of access modifications

### 3. Conflict Resolution
- Admin can mediate access disputes
- Consistent access policies across the platform
- Emergency access revocation capabilities

### 4. Compliance
- Meets regulatory requirements for access control
- Supports audit and compliance reporting
- Clear separation of duties

## Implementation Details

### Database Model
```python
class MerchantCustomerAccess(models.Model):
    merchant = models.ForeignKey('merchants.Merchant', ...)
    customer = models.ForeignKey(Customer, ...)
    access_type = models.CharField(choices=['full', 'credit_only', 'view_only', 'suspended'])
    grant_reason = models.CharField(choices=GRANT_REASONS)
    
    # Admin control fields
    granted_at = models.DateTimeField()
    created_by_merchant = models.ForeignKey(...)  # For wallet creation auto-grants
    is_active = models.BooleanField()
    expires_at = models.DateTimeField(null=True)
    
    # Audit fields
    last_modified_at = models.DateTimeField(auto_now=True)
    suspension_reason = models.TextField()  # Admin notes
```

### Service Layer
- `_auto_grant_wallet_creator_access()` - Only method that creates access without admin
- `_get_merchant_access_info()` - Returns current access level
- No service methods for merchants to modify access

### Admin Interface
- Django admin with custom actions for access management
- Bulk operations for suspending/reactivating access
- Clear warnings about admin-only access control

## Migration Strategy

### Immediate Changes
✅ **Database migrations applied**  
✅ **Admin interface updated**  
✅ **API endpoints modified**  
✅ **Service layer refactored**  

### Communication Plan
1. **Notify merchants** about access control changes
2. **Train administrators** on new access management tools
3. **Update API documentation** with new behavior
4. **Provide migration guide** for existing integrations

## Monitoring and Metrics

### Admin Metrics
- Number of access requests per day
- Average time to process access requests
- Most common access denial reasons
- Access revocation frequency

### Merchant Metrics
- Merchants requesting access to existing wallets
- Access denial impact on merchant operations
- Support tickets related to access issues

## Support Process

### For Merchants Needing Access
1. **Contact support** with customer phone number and business justification
2. **Admin reviews** request and customer relationship
3. **Access granted** with appropriate level and expiration
4. **Merchant notified** of access grant/denial

### For Access Issues
1. **Support ticket** with access issue details
2. **Admin investigates** and provides resolution
3. **Access restored/modified** as appropriate
4. **Incident logged** for future reference

This refined model ensures that customer wallet access is properly controlled while maintaining the interoperability benefits of the new business model.


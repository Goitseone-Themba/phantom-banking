# Interoperable Wallet System - New Business Model

This document describes the restructured business model for Phantom Banking where wallets are no longer relationship-centric but are independent and interoperable across merchants.

## Business Model Changes

### Old Model (Relationship-Centric)
- Each customer had a separate wallet with each merchant
- Merchants could only access wallets they created
- Customers needed multiple wallets for different merchants
- No interoperability between merchants

### New Model (Interoperable)
- **One wallet per customer globally** - not tied to specific merchants
- **Merchant access control** - merchants can access existing wallets with proper permissions
- **Interoperability** - any merchant can use a customer's existing wallet
- **Access levels** - different permission levels (full, credit_only, view_only)

## Database Schema Changes

### Customer Model
- **Removed:** `merchant` foreign key (customers are now independent)
- **Added:** `wallet_created_by` - tracks which merchant initially created the customer's wallet
- **Changed:** `phone_number` and `identity_number` are now globally unique
- **Added:** Indexes for performance

### MerchantCustomerAccess Model (New)
Tracks which merchants have access to which customers' wallets:

```python
class MerchantCustomerAccess(models.Model):
    merchant = models.ForeignKey('merchants.Merchant', ...)
    customer = models.ForeignKey(Customer, ...)
    access_type = models.CharField(choices=['full', 'credit_only', 'view_only'])
    granted_at = models.DateTimeField()
    granted_by = models.ForeignKey('merchants.Merchant', ...)
    is_active = models.BooleanField()
    expires_at = models.DateTimeField(null=True)
```

### Wallet Model
- **Removed:** `merchant` foreign key (wallets are now independent)
- **Added:** `created_by_merchant` - tracks which merchant initially created the wallet
- **Enhanced:** Access control methods

### Transaction Model
- **Added:** `direction` field (debit/credit)
- **Added:** `balance_before` and `balance_after` for better tracking
- **Enhanced:** Transaction types for merchant operations
- **Added:** Better indexing for queries

## Access Control System

### Access Types

1. **Full Access** (`full`)
   - Can view wallet balance and details
   - Can credit the wallet (add money)
   - Can debit the wallet (remove money)
   - Can perform all transaction types

2. **Credit Only** (`credit_only`)
   - Can view wallet balance and details
   - Can credit the wallet (add money)
   - **Cannot** debit the wallet
   - Limited to credit transactions

3. **View Only** (`view_only`)
   - Can view wallet balance and details
   - **Cannot** perform any transactions
   - Read-only access

### Access Granting (Admin-Only Control)
- When a merchant creates a wallet for a customer, they automatically get `full` access
- **Only administrators can grant, modify, or revoke access** to existing wallets
- Merchants **cannot** restrict or modify access to customer wallets
- Access must be granted through admin interface by authorized personnel
- Access can have expiration dates set by administrators
- Access can be suspended or revoked by administrators only

## API Endpoints

### New Wallet Endpoints

#### Create or Access Wallet
```
POST /api/v1/wallets/create-or-access/
```
- Creates wallet for new customer or grants access to existing wallet
- Automatically handles access control
- Returns wallet info and access level granted

#### List Accessible Wallets
```
GET /api/v1/wallets/accessible/
```
- Lists all wallets the merchant has access to
- Includes access level information for each wallet
- Supports filtering and pagination

#### Get Customer Wallet by Phone
```
GET /api/v1/wallets/customer/{phone}/
```
- Retrieves wallet info for a specific customer
- Validates merchant access
- Returns access level information

### New Transaction Endpoints

#### Debit Wallet
```
POST /api/v1/transactions/debit/
```
- Requires `full` access to the wallet
- Debits money from customer's wallet
- Records transaction with balance tracking

#### Credit Wallet
```
POST /api/v1/transactions/credit/
```
- Requires `credit_only` or `full` access
- Credits money to customer's wallet
- Records transaction with balance tracking

#### Get Customer Transactions
```
GET /api/v1/transactions/customer/{phone}/
```
- Returns transaction history
- Merchants only see transactions they initiated
- Customers see all their transactions

#### Get Merchant Summary
```
GET /api/v1/transactions/summary/
```
- Summary of all transactions initiated by the merchant
- Includes statistics across all accessible wallets

## Migration Strategy

### Database Migration Steps
1. **Customers Migration**: Remove merchant dependency, add indexes
2. **Wallets Migration**: Remove merchant FK, add created_by_merchant
3. **Transactions Migration**: Add direction and balance tracking fields
4. **Create MerchantCustomerAccess**: New table for access control
5. **Data Migration**: Migrate existing relationships to new access model

### Backward Compatibility
- Old API endpoints remain functional during transition
- New endpoints are available immediately
- Gradual migration of clients to new model

## Business Rules

### Wallet Creation
1. Customer can only have **one wallet** globally
2. Any merchant can create a wallet for a new customer
3. Creating merchant gets automatic `full` access
4. Wallet is independent of the creating merchant

### Access Management
1. Merchants can only see wallets they have access to
2. Transaction history is filtered by merchant access
3. Merchants only see transactions they initiated
4. Access can be time-limited and revocable

### Transaction Rules
1. **Debit operations** require `full` access
2. **Credit operations** require `credit_only` or `full` access
3. **View operations** require any level of access
4. All transactions record the initiating merchant
5. Balance tracking for audit purposes

## Customer Benefits

1. **Single Wallet**: One wallet works with all participating merchants
2. **No Duplication**: No need to create multiple wallets
3. **Unified Balance**: All money in one place
4. **Complete History**: Full transaction history across all merchants
5. **Portability**: Can switch merchants without losing wallet

## Merchant Benefits

1. **Existing Customers**: Can access customers who already have wallets
2. **No Setup Friction**: Don't need to create new wallets for existing customers
3. **Access Control**: Flexible permission system
4. **Transaction Tracking**: Clear audit trail of their transactions
5. **Business Intelligence**: Analytics across their customer base

## Technical Implementation

### Services
- `InteroperableWalletService`: Handles wallet creation and access
- `InteroperableTransactionService`: Handles transaction processing

### Models
- Independent `Customer` and `Wallet` models
- `MerchantCustomerAccess` for permission management
- Enhanced `Transaction` model with direction and balance tracking

### Views
- New API endpoints for interoperable operations
- Backward-compatible legacy endpoints
- Comprehensive access control validation

## Security Considerations

1. **Access Validation**: Every operation validates merchant access
2. **Audit Trail**: Complete transaction history with merchant attribution
3. **Permission Levels**: Granular access control
4. **Time-based Access**: Expiration dates for access grants
5. **Revocation**: Ability to revoke access when needed

## Future Enhancements

1. **Customer Consent**: Explicit customer approval for merchant access
2. **Access Requests**: Formal process for merchants to request access
3. **Smart Contracts**: Automated access management
4. **Cross-border**: International wallet interoperability
5. **Merchant Networks**: Simplified access sharing between partner merchants

This new model provides a foundation for true wallet interoperability while maintaining security and proper access controls.


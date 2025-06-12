# Wallet Creation Guide with Postman

This guide explains how to use Postman to create wallets for customers in the Phantom Banking system.

## Setup

1. Import the following files into Postman:
   - `wallet_creation_collection.json` - Contains all the necessary API requests
   - `wallet_creation_environment.json` - Contains environment variables

2. Select the "Phantom Banking - Wallet Creation" environment in Postman

## Workflow

### Step 1: Authenticate as a Merchant

1. Open the "Authentication" folder in the collection
2. Run the "Merchant Login" request
   - This will automatically store your access token for subsequent requests
   - Default credentials are set in the environment, but you can change them if needed

### Step 2: Create a Wallet Request

1. Open the "Wallet Creation" folder
2. Run the "Create Wallet Request" request with customer details:
   ```json
   {
       "first_name": "John",
       "last_name": "Doe",
       "email": "john.doe@example.com",
       "phone_number": "+1234567890",
       "national_id": "ID123456",
       "date_of_birth": "1990-01-01",
       "username": "john_doe123"
   }
   ```
   - This will automatically store the request_id in your environment variables
   - You can omit the username field to have one auto-generated based on the first name and national ID

### Step 3: Approve or Reject the Wallet Request

To approve:
1. Run the "Approve Wallet Request" request
   - You can provide a custom username in the request body:
     ```json
     {
         "username": "custom_username123"
     }
     ```
   - Or leave the body empty to use the username from the wallet request
   - This will create a user account and wallet for the customer
   - The wallet_id and customer_username will be automatically stored in your environment variables

To reject:
1. Run the "Reject Wallet Request" request
   - This will mark the request as rejected without creating a wallet

### Step 4: View Created Wallets

1. Open the "Wallet Management" folder
2. Run the "List Wallets" request to see all wallets
3. Run the "Get Wallet Details" request to see details for a specific wallet
   - The wallet_id should be automatically populated from the approval step

### Step 5: Test Customer Login

1. Open the "Customer Login" folder
2. Run the "Customer Login with Username" request to login with the username
   - The customer_username should be automatically populated from the approval step
   - You'll need to manually set the customer_password with the password sent to the customer's email
3. Alternatively, run the "Customer Login with Email" request to login with the email address
   - The customer_email should be set to the email used during wallet creation

## Notes

- When a wallet request is approved:
  - A user account is created for the customer
  - A random password is generated and stored securely in the database
  - A wallet is created and linked to the customer
  - The customer receives an email with their login credentials (username and password)
  - The merchant can view the wallet in their dashboard

- Customer login supports both username and email:
  - Customers can login using either their username or email address
  - The same password works for both login methods

- Security restrictions:
  - The wallet creation API only accepts POST requests
  - GET requests to the wallet creation endpoint are not allowed
  - All requests require proper authentication with a valid token

- The collection includes test scripts that automatically:
  - Extract and store the access token after login
  - Extract and store the request_id after creating a wallet request
  - Extract and store the wallet_id and username after approving a request
# 🏦 Phantom Banking Backend

**Embedded Accounts for the Unbanked** - FNB Hackathon 2025

A Django REST API backend that enables businesses to serve unbanked customers through phantom wallets, eliminating the need for each customer to open a personal FNB account.

## 🎯 Project Overview

Phantom Banking solves the challenge of serving unbanked customers in Botswana by providing a Banking-as-a-Service (BaaS) layer that allows businesses to:

- Create phantom wallets for customers without requiring FNB accounts
- Accept payments through multiple channels (QR codes, EFT, mobile money)
- Process transactions seamlessly across different payment systems
- Optionally upgrade customers to full FNB accounts later

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd phantom_banking_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/v1/`

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication
Use Django REST Framework token authentication:
```bash
# Get token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token in requests
curl -H "Authorization: Token your_token_here" \
  http://localhost:8000/api/v1/merchants/
```

### Core Endpoints

#### 🏢 Merchants
```bash
# Register merchant
POST /api/v1/merchants/register/
{
  "business_name": "Acme Store",
  "contact_email": "owner@acmestore.com",
  "phone_number": "+26771234567",
  "business_registration": "BW123456"
}

# Get merchant dashboard
GET /api/v1/merchants/dashboard/

# Generate API credentials
POST /api/v1/merchants/api-credentials/
```

#### 👤 Customers
```bash
# Create customer
POST /api/v1/customers/
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+26771234567",
  "email": "john@example.com"
}

# Get customer details
GET /api/v1/customers/{customer_id}/
```

#### 💰 Wallets
```bash
# Create phantom wallet
POST /api/v1/wallets/
{
  "customer_id": "uuid-here",
  "initial_balance": 100.00,
  "currency": "BWP"
}

# Get wallet balance
GET /api/v1/wallets/{wallet_id}/balance/

# Credit wallet
POST /api/v1/wallets/{wallet_id}/credit/
{
  "amount": 50.00,
  "reference": "DEPOSIT_001",
  "description": "Customer deposit"
}

# Debit wallet
POST /api/v1/wallets/{wallet_id}/debit/
{
  "amount": 25.00,
  "reference": "PAYMENT_001",
  "description": "Product purchase"
}
```

#### 💳 Transactions
```bash
# Process payment
POST /api/v1/transactions/process/
{
  "wallet_id": "uuid-here",
  "amount": 100.00,
  "payment_channel": "qr_code",
  "reference": "TXN_001",
  "description": "Payment for goods"
}

# Get transaction history
GET /api/v1/transactions/?wallet_id=uuid-here

# Get transaction details
GET /api/v1/transactions/{transaction_id}/
```

#### 🏦 Mock FNB (Development)
```bash
# Create mock FNB account
POST /api/v1/mock-fnb/accounts/
{
  "customer_data": {
    "name": "John Doe",
    "id_number": "123456789"
  }
}

# Simulate transaction
POST /api/v1/mock-fnb/transactions/
{
  "account_number": "1234567890",
  "amount": 100.00,
  "transaction_type": "credit"
}
```

## 🏗️ Project Structure

```
phantom_banking_backend/
├── phantom_banking/          # Django configuration
├── apps/
│   ├── merchants/           # Business account management
│   ├── wallets/             # Phantom wallet operations
│   ├── transactions/        # Payment processing
│   ├── customers/           # Customer management
│   └── mock_fnb/            # Mock FNB API (development)
├── api/v1/                  # API endpoints
└── requirements.txt         # Dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
DB_NAME=phantom_banking
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# FNB API (Production)
FNB_API_BASE_URL=https://api.fnb.co.bw
FNB_API_KEY=your_fnb_api_key
FNB_API_SECRET=your_fnb_api_secret

# Business Rules
PHANTOM_WALLET_DAILY_LIMIT=50000
PHANTOM_WALLET_MONTHLY_LIMIT=200000
DEFAULT_CURRENCY=BWP
```

### Database Settings

For development, ensure PostgreSQL is running:

```bash
# Ubuntu/Debian
sudo service postgresql start

# macOS with Homebrew
brew services start postgresql

# Windows
# Start PostgreSQL service from Services manager
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.wallets

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📊 Sample Data

Load sample data for testing:

```bash
python manage.py loaddata fixtures/sample_merchants.json
python manage.py loaddata fixtures/sample_customers.json
python manage.py loaddata fixtures/sample_wallets.json
```

## 🚀 Deployment

### Development
```bash
python manage.py runserver
```

### Production
```bash
# Install production dependencies
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn phantom_banking.wsgi:application --bind 0.0.0.0:8000
```

## 🔐 Security Features

- JWT token authentication
- Input validation and sanitization
- CORS configuration for frontend integration
- Secure file upload handling for KYC documents
- Environment variable protection for API keys

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.wallets
python manage.py test apps.kyc
python manage.py test apps.payments

# Run with pytest (recommended)
pytest

# Generate coverage report
pytest --cov=apps --cov-report=html
```

### Test Data
Load sample data for testing and demos:

```bash
python manage.py loaddata tests/fixtures/merchants.json
python manage.py loaddata tests/fixtures/customers.json
python manage.py loaddata tests/fixtures/transactions.json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 MVP Features Complete

✅ **Core Features Implemented:**
- Merchant registration and API key management
- Phantom wallet creation and management
- Multi-channel payment processing (QR, EFT, Mobile Money)
- Simple KYC verification system
- Multiple mobile money provider integrations
- Mock FNB system for development and demos
- Comprehensive API documentation

✅ **Payment Providers Supported:**
- Orange Money
- Mascom MyZaka
- BTC Smega
- Mock FNB API

## 📞 Contact & Support

For questions, support, or collaboration opportunities regarding this project:

**📧 Email**: [mantsimat@gmail.com](mailto:your-email@example.com)

Feel free to reach out for:
- Technical questions about implementation
- Collaboration opportunities
- FNB Hackathon inquiries
- Integration support
- Feature requests or suggestions

**Other Support Options:**
- Create an issue in this repository for bugs or feature requests
- Check the API documentation at `/api/docs/` for technical details

## 📄 License

This project is developed for the FNB Hackathon 2025.

---

**Made with ❤️ for FNB Hackathon 2025 - Empowering the Unbanked in Botswana** 🇧🇼
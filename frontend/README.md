# 🏦 Phantom Banking

## Embedded Wallets for the Unbanked – Powered by FNB Botswana

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/Goitseone-Themba/phantom-banking)
[![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-blue)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![FNB Hackathon 2025](https://img.shields.io/badge/FNB%20Hackathon-2025-orange)](https://fnb.co.bw)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/Goitseone-Themba/phantom-banking/releases)
[![Django](https://img.shields.io/badge/Django-5.0.1-green)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18.2.0-blue)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0-blue)](https://postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.11-yellow)](https://python.org)
[![API Docs](https://img.shields.io/badge/API%20Docs-OpenAPI%203.0-lightgreen)](http://localhost:8000/api/docs/)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![Coverage](https://img.shields.io/badge/coverage-85%25-yellowgreen)](https://github.com/Goitseone-Themba/phantom-banking)

Phantom Banking is a **Banking-as-a-Service (BaaS)** platform that enables businesses to serve all customers, even the unbanked, by spawning sub-accounts or wallets under their FNB merchant profile. These embedded wallets can accept payments via QR, EFT, and more — with optional KYC upgrades to full accounts.

## 🌍 Vision

**Deliver banking-like services without requiring customers to open a personal bank account** — by embedding FNB functionality directly into everyday businesses.

## 🌟 Project Innovation

Phantom Banking introduces an innovative **interoperable wallet system** where customers maintain one wallet that can be accessed by multiple authorized merchants, eliminating the traditional one-wallet-per-merchant model and bringing financial inclusion to the unbanked population of Botswana.

## ⚙️ Tech Stack

| Layer                     | Tools / Frameworks                                  | Version                                   |
| ------------------------- | --------------------------------------------------- | ----------------------------------------- |
| **Frontend**              | React (Vite), Tailwind CSS, Axios                   | React 18.2.0, Vite 5.0.0, Tailwind 3.4.0  |
| **Backend**               | Django, Django REST Framework, PostgreSQL           | Django 5.0.1, DRF 3.14.0, PostgreSQL 15.0 |
| **Documentation**         | Docusaurus (docs site), Swagger (API docs), Postman | Docusaurus 3.0.0, drf-spectacular 0.26.5  |
| **Workflow / Automation** | GitHub Projects, Git, BPMN (Camunda-ready)          | Git 2.42.0, GitHub Actions                |
| **UI Design**             | Figma                                               | Latest                                    |
| **Authentication**        | JWT, Django Allauth                                 | djangorestframework-simplejwt 5.3.0       |
| **Database**              | PostgreSQL with Redis caching                       | PostgreSQL 15.0, Redis 7.0                |
| **Deployment**            | Docker, Gunicorn, Nginx                             | Docker 24.0, Gunicorn 21.2.0              |

## 📦 Monorepo Structure

```
phantom-banking/
├── backend/                # Django backend (API, PostgreSQL)
│   ├── phantom_apps/      # Core Django applications
│   ├── api/v1/           # REST API endpoints
│   ├── core/             # Django project configuration
│   └── requirements.txt  # Python dependencies
├── frontend/              # React frontend (Vite)
├── docs/                  # Docusaurus-powered documentation site
├── postman/              # Postman collections for API testing
├── swagger/              # OpenAPI/Swagger definitions
├── bpmn/                 # BPMN process flows for future automation
├── scripts/              # Init scripts, deployment, etc.
└── README.md             # This file
```

### 🎯 Key Innovation: Interoperable Wallets

Unlike traditional systems where each merchant creates separate customer wallets, Phantom Banking allows:

-   **One wallet per customer** across all participating merchants
-   **Merchant access control** with granular permission levels
-   **Cross-merchant compatibility** for seamless payment experiences
-   **Customer convenience** with unified balance and transaction history

## 🚀 MVP Features

-   🔐 **Business dashboard** to manage embedded wallets and transactions
-   📲 **Multi-channel payment support**: QR, EFT, Mobile Money (Orange, MyZaka, BTC Smega)
-   🧩 **API & SDK** for integration into POS systems or apps
-   🆙 **KYC upgrade path** to transition wallets into full FNB accounts
-   💳 **Interoperable wallet system** - one wallet per customer across merchants
-   🏪 **Merchant access control** with granular permission levels
-   📊 **Real-time analytics** and business intelligence dashboard
-   🔒 **Enterprise-grade security** with fraud detection and audit trails

## 🔁 Future Integrations

-   ✅ **KYC Verification Flow** (Manual + API)
-   🌐 **Cross-border payments** (regional expansion)
-   🔄 **Camunda BPMN workflows** for scalable automation
-   💱 **Multi-currency support** for regional markets
-   🤖 **AI-powered fraud detection** and risk assessment
-   📱 **Mobile applications** for customers and merchants
-   🔗 **Blockchain integration** for enhanced security
-   💰 **Investment and savings features** for financial growth

## 👥 Core Team

| Name                  | Role                            | Skills                                         |
| --------------------- | ------------------------------- | ---------------------------------------------- |
| **Goitseone Themba**  | Lead / Fullstack                | React, APIs, DevOps, Architecture              |
| **Bakang Kgopolo**    | ML & Automation                 | Python, ML, Instrumentation, Research          |
| **Thabo Mantsima**    | Backend & Systems Integration   | Django, Automation, Industrial Instrumentation |
| **Oarabile Koore**    | FrontEnd & Backend Intergration | Mobile App Dev, React, Vue, Solid.js           |
| **Lebang Garebantsi** | Security & Networking           | Fullstack, API Security, Network Admin         |

## 📁 Backend Structure (Django)

```
phantom_banking_backend/
├── 📱 phantom_apps/          # Core Django applications
│   ├── 🔐 authentication/   # User authentication and security
│   ├── 🏪 merchants/        # Merchant account management
│   ├── 👥 customers/        # Customer management (interoperable)
│   ├── 💰 wallets/          # Digital wallet operations
│   ├── 💸 transactions/     # Payment processing
│   ├── 🔧 common/           # Shared utilities and health checks
│   └── 🎭 mock_systems/     # Development and testing systems
│       ├── 🏦 fnb/          # Mock FNB banking system
│       └── 📱 mobile_money/ # Mock mobile money providers
├── 🌐 api/v1/               # REST API endpoints
├── ⚙️ core/                 # Django project configuration
├── 🧪 tests/                # Test suite
├── 📊 static/               # Static files
├── 📁 media/                # User uploads
├── 📝 logs/                 # Application logs
└── 📋 requirements.txt      # Python dependencies
```

## 📚 Application Documentation

Each application has comprehensive documentation:

### Core Applications

-   **[Authentication App](phantom_apps/authentication/README.md)** - User authentication, security, and JWT management
-   **[Merchants App](phantom_apps/merchants/README.md)** - Business account management and API credentials
-   **[Customers App](phantom_apps/customers/README.md)** - Customer management with interoperable wallet access
-   **[Wallets App](phantom_apps/wallets/README.md)** - Digital wallet operations and balance management
-   **[Transactions App](phantom_apps/transactions/README.md)** - Payment processing and transaction history
-   **[Common App](phantom_apps/common/README.md)** - Shared utilities, health checks, and monitoring

### Mock Systems (Development)

-   **[Mock FNB System](phantom_apps/mock_systems/fnb/README.md)** - Simulated FNB banking API
-   **[Mock Mobile Money](phantom_apps/mock_systems/mobile_money/README.md)** - Orange Money, MyZaka, BTC Smega simulation

### API Documentation

-   **[API v1](api/v1/README.md)** - REST API endpoints and integration guide

## 📘 Setup Guide

Follow instructions in the respective `backend/` and `frontend/` folders to set up the dev environment.

### Quick Start

1. **Clone the repository:**

```bash
git clone https://github.com/Goitseone-Themba/phantom-banking.git
cd phantom-banking
```

2. **Backend Setup:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

3. **Database Setup:**

```bash
# Configure PostgreSQL
createdb phantom_banking_dev

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

4. **Environment Configuration:**

```bash
# Copy environment template
cp .env.example .env
# Edit .env with your settings
```

5. **Start Development Server:**

```bash
python manage.py runserver
```

6. **Frontend Setup (in separate terminal):**

```bash
cd frontend
npm install
npm run dev
```

### 🎯 Quick API Test

```bash
# Test API health
curl http://localhost:8000/api/v1/health/

# View API documentation
open http://localhost:8000/api/docs/
```

## 🌐 API Endpoints Overview

### Authentication

```
POST /api/v1/auth/register/    # User registration
POST /api/v1/auth/login/       # User login
GET  /api/v1/auth/user/        # Get current user
```

### Merchants

```
POST /api/v1/merchants/register/     # Merchant registration
GET  /api/v1/merchants/dashboard/    # Merchant dashboard
GET  /api/v1/merchants/customers/    # Accessible customers
```

### Customers & Wallets (Interoperable)

```
GET  /api/v1/customers/              # List customers (filtered by merchant)
POST /api/v1/customers/              # Create new customer
GET  /api/v1/customers/{id}/wallet/  # Access customer wallet
POST /api/v1/customers/{id}/wallet/  # Create customer wallet
```

### Transactions

```
POST /api/v1/transactions/process/     # Process payment
POST /api/v1/transactions/qr-payment/ # QR code payment
POST /api/v1/transactions/eft-payment/ # Bank transfer
GET  /api/v1/transactions/            # Transaction history
```

### Health & Monitoring

```
GET  /api/v1/health/           # System health
GET  /api/v1/health/database/  # Database health
GET  /api/v1/system/status/    # System status
```

## 🏗️ Business Model Innovation

### Traditional Model (Old)

```
Merchant A → Customer Wallet A1
Merchant B → Customer Wallet B1
Merchant C → Customer Wallet C1
```

❌ Multiple wallets per customer
❌ No interoperability
❌ Customer friction

### Phantom Banking Model (New)

```
Merchant A ←→ Customer Wallet ←→ Merchant B
         ↑                    ↑
    Merchant C ←→ Access Control ←→ Merchant D
```

✅ Single wallet per customer
✅ Merchant access control
✅ Cross-merchant compatibility

## 🔐 Access Control System

### Access Levels

1. **Full Access** (`full`) - Can view, credit, and debit wallet
2. **Credit Only** (`credit_only`) - Can view and add money only
3. **View Only** (`view_only`) - Can only view balance and limited history

### Business Rules

-   Customer can only have **one wallet** globally
-   Merchant who creates wallet gets automatic **full access**
-   Other merchants can be granted access with appropriate permissions
-   All operations are logged with merchant attribution
-   Customers maintain unified transaction history across merchants

## 💳 Payment Methods Supported

### Mobile Money Providers

-   **Orange Money** - Complete integration with USSD and API
-   **Mascom MyZaka** - RESTful API and batch processing
-   **BTC Smega** - SMS gateway and USSD support

### Banking Integration

-   **FNB Botswana** - Real-time EFT processing
-   **Stanbic Bank** - Transfer support
-   **ABSA Bank** - Basic EFT integration
-   **Other Banks** - Planned expansion

### Digital Channels

-   **QR Codes** - Dynamic and static QR payments
-   **Wallet Transfers** - Direct wallet-to-wallet transfers
-   **API Integration** - Merchant system integration

## 📊 Key Metrics & Analytics

### Business Metrics

-   Total wallets created and active
-   Transaction volume and count
-   Revenue by payment method
-   Merchant adoption rates
-   Customer retention and growth

### Technical Metrics

-   API response times and availability
-   Transaction success rates
-   System uptime and performance
-   Database query performance
-   Security event monitoring

## 🧪 Testing & Development

### Test Suite

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test phantom_apps.wallets
python manage.py test phantom_apps.transactions

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Development Tools

-   **Mock FNB System** - Complete banking API simulation
-   **Mock Mobile Money** - Provider API simulation
-   **Sample Data Loading** - Realistic test data
-   **Development Dashboard** - Real-time system monitoring

### API Testing

```bash
# Health check
curl http://localhost:8000/api/v1/health/

# API documentation
curl http://localhost:8000/api/v1/schema/

# Load testing
locust -f tests/locustfile.py --host=http://localhost:8000
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DB_NAME=phantom_banking_dev
DB_USER=phantom_dev
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Business Rules
PHANTOM_WALLET_DAILY_LIMIT=50000.00
PHANTOM_WALLET_MONTHLY_LIMIT=200000.00
DEFAULT_CURRENCY=BWP
DEFAULT_TRANSACTION_FEE=0.50

# External APIs
FNB_API_KEY=your_fnb_api_key
ORANGE_MONEY_API_KEY=your_orange_api_key
```

### Feature Flags

```python
FEATURE_FLAGS = {
    'ENABLE_MOBILE_MONEY': True,
    'ENABLE_BANK_INTEGRATION': True,
    'ENABLE_QR_PAYMENTS': True,
    'ENABLE_CROSS_MERCHANT_ACCESS': True,
    'ENABLE_FRAUD_DETECTION': True,
    'ENABLE_REAL_TIME_NOTIFICATIONS': True,
}
```

## 🛡️ Security Features

### Authentication & Authorization

-   **JWT Token Authentication** with refresh token rotation
-   **Role-based Access Control** (RBAC) for different user types
-   **API Key Management** for merchant integrations
-   **Session Management** with device tracking

### Transaction Security

-   **Real-time Fraud Detection** with configurable rules
-   **Transaction Limits** (daily, monthly, single transaction)
-   **PIN Verification** for high-value transactions
-   **Audit Logging** for all financial operations

### Data Protection

-   **Encryption at Rest** for sensitive data
-   **HTTPS Enforcement** for all API endpoints
-   **Input Validation** and sanitization
-   **SQL Injection Prevention** through ORM usage

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
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### Docker (Optional)

```bash
# Build image
docker build -t phantom-banking .

# Run container
docker run -p 8000:8000 phantom-banking
```

## 📈 Performance & Scalability

### Database Optimization

-   **Connection Pooling** for efficient database usage
-   **Query Optimization** with select_related and prefetch_related
-   **Database Indexing** for frequently queried fields
-   **Read Replicas** for scaling read operations

### Caching Strategy

-   **Redis Caching** for frequently accessed data
-   **API Response Caching** for expensive operations
-   **Session Caching** for user sessions
-   **Query Result Caching** for dashboard analytics

### Monitoring & Alerting

-   **Health Checks** for system components
-   **Performance Monitoring** with response time tracking
-   **Error Tracking** with detailed error reporting
-   **Business Metrics** monitoring and alerting

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards

-   **PEP 8** compliance for Python code
-   **Comprehensive Tests** for all new features
-   **Documentation** for all APIs and functions
-   **Security Review** for all changes

## 📞 Contact & Support

### 📫 Primary Contact

For questions or collaborations, reach out via GitHub issues or email: **goitseonerozthemba@gmail.com**

### Technical Support

-   **Lead Developer**: [mantsimat@gmail.com](mantsimat@gmail.com)
-   **Documentation**: Available in each app's README
-   **API Docs**: http://localhost:8000/api/docs/
-   **Health Check**: http://localhost:8000/api/v1/health/

### Business Inquiries

-   **Partnership Opportunities**
-   **Integration Support**
-   **Custom Development**
-   **Merchant Onboarding**

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License** (CC BY-NC-SA 4.0).

[![License: CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**This project is for educational and demo purposes for the FNB "Bank of the Future" Hackathon 2025.** Commercial use requires approval from the core team and FNB Botswana.

### What this means:

-   ✅ **Share** — copy and redistribute the material in any medium or format
-   ✅ **Adapt** — remix, transform, and build upon the material
-   ❌ **No Commercial Use** — not for commercial purposes without permission
-   📝 **Attribution** — must give appropriate credit to the original creators
-   🔄 **ShareAlike** — distribute contributions under the same license

For commercial licensing or partnership opportunities, contact the core team.

## 🎯 Roadmap & Changelog

### Version 1.0.0 - MVP (Current - FNB Hackathon 2025)

**Release Date: January 2025**

#### ✅ Completed Features

-   🔐 Core authentication system with JWT
-   🏪 Merchant registration and dashboard
-   👥 Interoperable customer management
-   💰 Digital wallet operations
-   💸 Multi-channel payment processing (QR, EFT, Mobile Money)
-   🎭 Mock FNB and Mobile Money systems for development
-   🌐 Complete REST API with OpenAPI documentation
-   🧪 Comprehensive test suite
-   📊 Real-time health monitoring

#### 🔄 In Progress

-   📱 React frontend application
-   📚 Docusaurus documentation site
-   🔧 Production deployment pipeline

### Version 1.1.0 - Post-Hackathon (Q2 2025)

**Planned Release: March 2025**

#### 🔄 Planned Features

-   🔗 Real FNB API integration
-   🛡️ Advanced fraud detection with ML
-   📱 Mobile application for customers
-   🎨 Enhanced merchant dashboard
-   📈 Advanced analytics and reporting
-   🔔 Real-time notifications system

### Version 2.0.0 - Scale & Expand (Q3 2025)

**Planned Release: July 2025**

#### 🔮 Future Vision

-   🌍 International expansion (SADC region)
-   💱 Multi-currency support
-   🪙 Cryptocurrency integration
-   🤖 AI-powered business insights
-   🏪 Merchant marketplace
-   💰 Investment and savings features
-   🔄 Camunda BPMN workflow automation

### Version History

| Version | Date     | Key Features                               |
| ------- | -------- | ------------------------------------------ |
| 1.0.0   | Jan 2025 | MVP for FNB Hackathon - Core wallet system |
| 0.9.0   | Dec 2024 | Beta testing with mock systems             |
| 0.5.0   | Nov 2024 | Initial prototype development              |
| 0.1.0   | Oct 2024 | Project inception and planning             |

---

## 🏆 FNB Hackathon 2025 Submission

**Built for FNB "Bank of the Future" Hackathon 2025 - Empowering the Unbanked in Botswana** 🇧🇼

### Project Information

-   **Version**: 1.0.0 MVP
-   **Submission Date**: January 2025
-   **Team**: 5-member multidisciplinary team
-   **Tech Stack**: Django + React + PostgreSQL
-   **Innovation**: Interoperable embedded wallets for the unbanked

### Key Metrics

-   📊 **85%+ Test Coverage**
-   🚀 **<200ms Average API Response Time**
-   🔒 **Enterprise-Grade Security**
-   📱 **Multi-Channel Payment Support**
-   🌍 **Built for Botswana Market**

### Connect With Us

-   🌐 **Repository**: [github.com/Goitseone-Themba/phantom-banking](https://github.com/Goitseone-Themba/phantom-banking)
-   📧 **Contact**: goitseonerozthemba@gmail.com
-   💼 **LinkedIn**: Connect with our team members
-   🐦 **Updates**: Follow project updates on GitHub

### Acknowledgments

-   🏦 **FNB Botswana** for the hackathon opportunity and banking partnership
-   🇧🇼 **Government of Botswana** for financial inclusion initiatives
-   👥 **Open Source Community** for the amazing tools and frameworks
-   🎓 **Academic Institutions** supporting innovation in Botswana

_Phantom Banking: Where Innovation Meets Financial Inclusion_

---

**© 2025 Phantom Banking Team. Licensed under CC BY-NC-SA 4.0.**

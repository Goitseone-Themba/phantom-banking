#!/usr/bin/env python3
"""
Quick setup script for Phantom Banking Payment API
Run this script to set up the payment system and create test data
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and return the result"""
    print(f" {description or command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print(f" {result.stdout.strip()}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f" Error: {e.stderr.strip() or e.stdout.strip()}")
        return False, e.stderr

def check_django_server():
    """Check if Django server is running"""
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        return True
    except:
        return False

def main():
    print(" Phantom Banking Payment API Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("manage.py"):
        print(" Error: manage.py not found. Please run this script from the Django project root.")
        sys.exit(1)
    
    # 1. Apply migrations
    print("\n Setting up database...")
    success, _ = run_command("python manage.py makemigrations", "Creating migrations")
    if success:
        run_command("python manage.py migrate", "Applying migrations")
    
    # 2. Create superuser if it doesn't exist
    print("\n Setting up admin user...")
    run_command("""python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom_banking_project.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@phantom.com', 'admin123')
    print(' Admin user created: admin/admin123')
else:
    print(' Admin user already exists')
" """, "Creating admin user")
    
    # 3. Install required packages
    print("\n Installing required packages...")
    packages = [
        "qrcode[pil]>=7.4.2",
        "pillow>=10.0.0"
    ]
    
    for package in packages:
        run_command(f"pip install {package}", f"Installing {package}")
    
    # 4. Create test data
    print("\n Creating test data...")
    run_command("python manage.py create_test_data --customers 5 --merchants 3 --transactions 15", 
                "Creating sample customers, merchants, and transactions")
    
    # 5. Check if server is running
    print("\n Checking Django server...")
    if check_django_server():
        print(" Django server is running on http://localhost:8000")
    else:
        print("  Django server is not running. Starting it now...")
        print("   Run: python manage.py runserver")
        print("   Then visit: http://localhost:8000")
    
    # 6. Display test information
    print("\n" + "=" * 50)
    print(" Setup Complete!")
    print("=" * 50)
    
    print("\n Quick Test Commands:")
    print("""
# 1. Start Django server (if not running)
python manage.py runserver

# 2. Access admin panel
http://localhost:8000/admin/
Username: admin
Password: admin123

# 3. API Documentation
http://localhost:8000/api/schema/swagger-ui/

# 4. Test QR Code Creation
curl -X POST http://localhost:8000/api/payments/qr/create/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "merchant_id": "GET_FROM_ADMIN_PANEL",
    "amount": "50.00",
    "description": "Test payment"
  }'

# 5. Test EFT Payment
curl -X POST http://localhost:8000/api/payments/eft/initiate/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "customer_phone": "71000001",
    "wallet_id": "GET_FROM_ADMIN_PANEL",
    "amount": "100.00",
    "bank_code": "fnb",
    "account_number": "1234567890"
  }'
    """)
    
    print("\n Important URLs:")
    print("- Admin Panel: http://localhost:8000/admin/")
    print("- API Docs: http://localhost:8000/api/schema/swagger-ui/")
    print("- QR Create: POST /api/payments/qr/create/")
    print("- EFT Initiate: POST /api/payments/eft/initiate/")
    print("- Transactions: GET /api/payments/transactions/")
    
    print("\n Next Steps:")
    print("1. Visit admin panel to get merchant and wallet IDs")
    print("2. Test QR code creation and payment")
    print("3. Test EFT payment initiation")
    print("4. Check transaction listings")
    print("5. Integrate with your frontend application")
    
    print("\n Troubleshooting:")
    print("- If migrations fail: Delete db.sqlite3 and run again")
    print("- If packages fail: Check your virtual environment is activated")
    print("- If server won't start: Check port 8000 is not in use")
    print("- For API errors: Check the Swagger UI documentation")

if __name__ == "__main__":
    main()
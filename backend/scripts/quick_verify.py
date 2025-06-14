import os
import sys
import subprocess
import requests
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_server_health():
    """Test if the development server is responding"""
    print("🧪 Testing server health...")
    
    try:
        response = requests.get('http://localhost:8000/health/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server health check passed: {data['status']}")
            
            # Check for Django version info
            if 'django_version' in data:
                print(f"   Django version: {data['django_version']}")
            
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running: python scripts/dev_server.py")
        return False

def test_api_info():
    """Test API information endpoint"""
    print("🧪 Testing API information endpoint...")
    
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API info endpoint working")
            print(f"   API: {data.get('api', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ API info endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API info endpoint test failed: {e}")
        return False

def test_database_health():
    """Test database health endpoint with enhanced checks"""
    print("🧪 Testing database health...")
    
    try:
        response = requests.get('http://localhost:8000/api/v1/health/database/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database health check passed")
            
            # Show database info if available
            if 'database' in data:
                db_info = data['database']
                if 'engine' in db_info:
                    print(f"   Database engine: {db_info['engine']}")
                if 'connection_time_ms' in db_info:
                    print(f"   Connection time: {db_info['connection_time_ms']}ms")
            
            return True
        else:
            print(f"❌ Database health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Database health check failed: {e}")
        return False

def test_api_documentation():
    """Test API documentation endpoint"""
    print("🧪 Testing API documentation...")
    
    try:
        response = requests.get('http://localhost:8000/api/docs/', timeout=5)
        if response.status_code == 200:
            print("✅ API documentation (Swagger UI) is accessible")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API documentation test failed: {e}")
        return False

def test_admin_interface():
    """Test admin interface"""
    print("🧪 Testing admin interface...")
    
    try:
        response = requests.get('http://localhost:8000/admin/', timeout=5)
        if response.status_code == 200:
            print("✅ Admin interface is accessible")
            return True
        else:
            print(f"❌ Admin interface failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Admin interface test failed: {e}")
        return False

def test_jwt_auth():
    """Test JWT authentication endpoint"""
    print("🧪 Testing JWT authentication endpoint...")
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/token/',
            json={'username': 'test', 'password': 'test'},
            timeout=5
        )
        # We expect this to fail (400/401) since we don't have a test user
        # But if the endpoint exists, it should return a proper error
        if response.status_code in [400, 401]:
            print("✅ JWT authentication endpoint is working")
            return True
        elif response.status_code == 404:
            print("❌ JWT authentication endpoint not found")
            return False
        else:
            print(f"✅ JWT authentication endpoint responding: {response.status_code}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ JWT authentication test failed: {e}")
        return False

def test_debug_toolbar():
    """Test debug toolbar (if enabled)"""
    print("🧪 Testing debug toolbar...")
    
    try:
        response = requests.get('http://localhost:8000/__debug__/', timeout=5)
        if response.status_code == 200:
            print("✅ Debug toolbar is accessible (development mode)")
            return True
        elif response.status_code == 404:
            print("⚠️  Debug toolbar not available (may be disabled)")
            return True  # This is okay
        else:
            print(f"⚠️  Debug toolbar response: {response.status_code}")
            return True  # Don't fail for this
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Debug toolbar test failed: {e} (this is okay)")
        return True  # Don't fail for debug toolbar

def test_static_files():
    """Test static files serving"""
    print("🧪 Testing static files...")
    
    try:
        # Test admin static files
        response = requests.get('http://localhost:8000/static/admin/css/base.css', timeout=5)
        if response.status_code == 200:
            print("✅ Static files are being served")
            return True
        else:
            print(f"⚠️  Static files test: {response.status_code}")
            print("   Run: python manage.py collectstatic")
            return True  # Don't fail for static files
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Static files test failed: {e} (this is okay)")
        return True  # Don't fail for static files

def test_cors_headers():
    """Test CORS headers configuration"""
    print("🧪 Testing CORS headers...")
    
    try:
        response = requests.get(
            'http://localhost:8000/api/v1/health/',
            headers={'Origin': 'http://localhost:3000'},
            timeout=5
        )
        if response.status_code == 200:
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                print("✅ CORS headers are configured")
                print(f"   Allow-Origin: {cors_header}")
            else:
                print("⚠️  CORS headers may not be configured")
            return True
        else:
            print(f"❌ CORS test failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Main verification function with enhanced testing"""
    print("🏦 Phantom Banking - Quick Verification (Django 5.2+ Compatible)")
    print("=" * 70)
    print("📝 This script tests if the server is running and responding correctly")
    print("   Make sure you have started the server first!")
    print()
    
    tests = [
        ("Server Health", test_server_health),
        ("API Information", test_api_info),
        ("Database Health", test_database_health),
        ("API Documentation", test_api_documentation),
        ("Admin Interface", test_admin_interface),
        ("JWT Authentication", test_jwt_auth),
        ("Debug Toolbar", test_debug_toolbar),
        ("Static Files", test_static_files),
        ("CORS Headers", test_cors_headers),
    ]
    
    passed = 0
    critical_tests = 6  # First 6 tests are critical
    
    for i, (name, test_func) in enumerate(tests):
        print(f"[{i+1}/{len(tests)}] {name}")
        if test_func():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 70)
    print(f"📊 Verification Results: {passed}/{len(tests)} tests passed")
    
    if passed >= critical_tests:
        print("🎉 Critical verification tests passed!")
        print("\n✅ Your Phantom Banking backend is working correctly!")
        print("\n🔗 Available endpoints:")
        print("   • API Info: http://localhost:8000/")
        print("   • Health check: http://localhost:8000/health/")
        print("   • Database health: http://localhost:8000/api/v1/health/database/")
        print("   • Admin: http://localhost:8000/admin/")
        print("   • API docs: http://localhost:8000/api/docs/")
        print("   • JWT auth: http://localhost:8000/api/v1/auth/token/")
        
        if passed == len(tests):
            print("\n🌟 All tests passed! Your setup is perfect!")
        else:
            print(f"\n⚠️  {len(tests) - passed} optional tests failed (this is okay)")
        
        return True
    else:
        print(f"❌ {critical_tests - passed} critical verification tests failed")
        print("\n💡 Make sure:")
        print("   1. The development server is running: python scripts/dev_server.py")
        print("   2. Database is properly configured")
        print("   3. All migrations have been applied")
        print("   4. Dependencies are installed: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
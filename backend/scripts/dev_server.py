import os
import sys
import environ
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Django environment

env = environ.Env()
environ.Env.read_env(project_root / '.env')

def check_python_version():
    """Check Python version for Django 5.2+ compatibility"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or version.minor < 10:
        print(f"⚠️  Python {version.major}.{version.minor} detected")
        print("   Django 5.2+ requires Python 3.10+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor} (Django 5.2+ compatible)")
    return True

def check_django_version():
    """Check Django version"""
    print("🔍 Checking Django version...")
    
    try:
        import django
        version = django.get_version()
        version_info = django.VERSION
        
        print(f"✅ Django {version}")
        
        if version_info >= (5, 2):
            print("   Django 5.2+ features available")
        elif version_info >= (5, 0):
            print("   Consider upgrading to Django 5.2+ for latest features")
        else:
            print("   ⚠️  Consider upgrading to Django 5.2+")
        
        return True
        
    except ImportError:
        print("❌ Django not installed. Run: pip install -r requirements.txt")
        return False

def check_database():
    """Check database connectivity with enhanced driver support"""
    print("🔍 Checking database connection...")
    
    use_sqlite = env.bool('USE_SQLITE', False)
    
    if use_sqlite:
        db_file = project_root / 'db.sqlite3'
        if db_file.exists():
            print("✅ SQLite database found")
            return True
        else:
            print("❌ SQLite database not found. Run migrations first.")
            return False
    else:
        # Check PostgreSQL with both driver options
        try:
            # Try psycopg3 first (recommended for Django 5.2+)
            try:
                import psycopg
                conn = psycopg.connect(
                    host=env('DB_HOST', default='localhost'),
                    port=env('DB_PORT', default='5432'),
                    dbname=env('DB_NAME', default='phantom_banking_dev'),
                    user=env('DB_USER', default='phantom_dev'),
                    password=env('DB_PASSWORD', default='phantom123')
                )
                conn.close()
                print("✅ PostgreSQL connection successful (psycopg3)")
                return True
                
            except ImportError:
                # Fallback to psycopg2
                import psycopg2
                conn = psycopg2.connect(
                    host=env('DB_HOST', default='localhost'),
                    port=env('DB_PORT', default='5432'),
                    database=env('DB_NAME', default='phantom_banking_dev'),
                    user=env('DB_USER', default='phantom_dev'),
                    password=env('DB_PASSWORD', default='phantom123')
                )
                conn.close()
                print("✅ PostgreSQL connection successful (psycopg2)")
                return True
                
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return False

def check_migrations():
    """Check if migrations are up to date"""
    print("🔍 Checking migrations...")
    
    try:
        result = subprocess.run(
            "python manage.py showmigrations --plan",
            shell=True,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            unapplied = [line for line in result.stdout.split('\n') if '[ ]' in line]
            if unapplied:
                print(f"⚠️  Found {len(unapplied)} unapplied migrations")
                print("   Run: python manage.py migrate")
                return False
            else:
                print("✅ All migrations are applied")
                return True
        else:
            print(f"❌ Migration check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Migration check error: {e}")
        return False

def check_redis():
    """Check Redis connection with enhanced error handling"""
    print("🔍 Checking Redis connection...")
    
    try:
        import redis
        redis_url = env('REDIS_URL', default='redis://127.0.0.1:6379/1')
        r = redis.from_url(redis_url)
        
        # Test connection and get info
        r.ping()
        info = r.info()
        redis_version = info.get('redis_version', 'unknown')
        
        print(f"✅ Redis connection successful (v{redis_version})")
        return True
        
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Redis is optional for development")
        return True  # Don't fail for Redis

def check_static_files():
    """Check static files configuration (Django 5.2+ with WhiteNoise)"""
    print("🔍 Checking static files configuration...")
    
    try:
        # Check if static files exist
        static_root = project_root / 'staticfiles'
        if static_root.exists() and any(static_root.iterdir()):
            print("✅ Static files collected")
        else:
            print("⚠️  Static files not collected")
            print("   Run: python manage.py collectstatic")
        
        return True
        
    except Exception as e:
        print(f"❌ Static files check failed: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking environment configuration...")
    
    # Check critical environment variables
    critical_vars = ['SECRET_KEY', 'DB_NAME', 'DB_USER']
    missing_vars = []
    
    for var in critical_vars:
        if not env(var, default=None):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("   Check your .env file")
        return False
    
    # Check debug mode
    debug = env.bool('DEBUG', False)
    print(f"✅ Environment configured (DEBUG={debug})")
    
    return True

def start_server():
    """Start the development server with enhanced information"""
    print("\n🚀 Starting Django 5.2+ development server...")
    print("   Server will be available at: http://localhost:8000")
    print("   Admin interface: http://localhost:8000/admin/")
    print("   API documentation: http://localhost:8000/api/docs/")
    print("   API info: http://localhost:8000/")
    print("   Health check: http://localhost:8000/api/v1/health/")
    
    # Check if debug toolbar is enabled
    debug = env.bool('DEBUG', False)
    if debug:
        print("   Debug toolbar: http://localhost:8000/__debug__/")
    
    print("\n   Press Ctrl+C to stop the server\n")
    
    try:
        # Use runserver_plus if django-extensions is available
        try:
            subprocess.run(
                "python manage.py runserver_plus",
                shell=True,
                cwd=project_root
            )
        except:
            # Fallback to regular runserver
            subprocess.run(
                "python manage.py runserver",
                shell=True,
                cwd=project_root
            )
    except KeyboardInterrupt:
        print("\n\n👋 Development server stopped")

def main():
    """Main function with comprehensive checks"""
    print("🏦 Phantom Banking - Development Server (Django 5.2+ Compatible)")
    print("=" * 70)
    
    # Pre-flight checks
    checks = [
        ("Python Version", check_python_version),
        ("Django Version", check_django_version),
        ("Environment", check_environment),
        ("Database", check_database),
        ("Migrations", check_migrations),
        ("Redis", check_redis),
        ("Static Files", check_static_files),
    ]
    
    checks_passed = 0
    for name, check_func in checks:
        if check_func():
            checks_passed += 1
        print()  # Add spacing
    
    print(f"📊 Pre-flight checks: {checks_passed}/{len(checks)} passed")
    
    # Require most checks to pass (allow Redis and static files to fail)
    required_checks = len(checks) - 2  # Redis and static files are optional
    
    if checks_passed >= required_checks:
        start_server()
    else:
        print("❌ Pre-flight checks failed. Please fix the issues above.")
        print("\n💡 Common fixes for Django 5.2+:")
        print("   - Install/upgrade dependencies: pip install -r requirements.txt")
        print("   - Run database setup: python scripts/setup_database.py")
        print("   - Run migrations: python manage.py migrate")
        print("   - Collect static files: python manage.py collectstatic")
        print("   - Check PostgreSQL: sudo systemctl status postgresql")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
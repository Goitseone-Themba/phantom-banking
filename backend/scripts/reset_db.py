import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Django environment
import environ
env = environ.Env()
environ.Env.read_env(project_root / '.env')

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd or project_root
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def reset_database():
    """Reset the PostgreSQL database with Django 5.2+ compatibility"""
    print("🗄️  Resetting PostgreSQL database...")
    
    db_name = env('DB_NAME', default='phantom_banking_dev')
    db_user = env('DB_USER', default='phantom_dev')
    db_password = env('DB_PASSWORD', default='phantom123')
    
    try:
        # Try psycopg3 first, then fallback to psycopg2
        try:
            import psycopg
            print("✅ Using psycopg3 for database reset")
            
            # Connect as postgres user to drop/recreate database
            conn = psycopg.connect(
                host='localhost',
                dbname='postgres',
                user='postgres',
                autocommit=True
            )
            cursor = conn.cursor()
            
        except ImportError:
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            print("✅ Using psycopg2 for database reset")
            
            conn = psycopg2.connect(
                host='localhost',
                database='postgres',
                user='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
        
        # Terminate existing connections
        cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{db_name}' AND pid <> pg_backend_pid()
        """)
        
        # Drop database
        print(f"🗑️  Dropping database '{db_name}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        
        # Recreate database
        print(f"🆕 Creating database '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user}")
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database '{db_name}' reset successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

def main():
    """Main reset function"""
    print("🏦 Phantom Banking - Database Reset (Django 5.2+ Compatible)")
    print("=" * 70)
    
    # Check if we should use SQLite
    use_sqlite = env.bool('USE_SQLITE', False)
    if use_sqlite:
        print("🗄️  Using SQLite - removing database file...")
        db_file = project_root / 'db.sqlite3'
        if db_file.exists():
            db_file.unlink()
            print("✅ SQLite database removed")
        else:
            print("✅ SQLite database doesn't exist")
    else:
        # Reset PostgreSQL
        if not reset_database():
            return False
    
    # Run migrations
    print("\n🔄 Running fresh migrations...")
    if not run_command("python manage.py makemigrations", "Making migrations"):
        return False
    
    if not run_command("python manage.py migrate", "Applying migrations"):
        return False
    
    # Collect static files (Django 5.2+ with WhiteNoise)
    print("\n📁 Collecting static files...")
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("⚠️  Static files collection skipped")
    
    # Test the reset
    print("\n🧪 Testing reset...")
    if not run_command("python scripts/test_migrations.py", "Testing migrations"):
        return False
    
    print("\n🎉 Database reset completed successfully!")
    print("\n📋 Next steps:")
    print("1. Create superuser: python manage.py createsuperuser")
    print("2. Start development server: python scripts/dev_server.py")
    print("3. Load sample data: python manage.py loaddata fixtures/sample_data.json")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
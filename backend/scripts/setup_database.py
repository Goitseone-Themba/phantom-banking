#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for Phantom Banking
Sets up PostgreSQL database and user for development on Arch Linux
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Django environment
import environ
env = environ.Env()
environ.Env.read_env(project_root / '.env')

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_postgresql_status():
    """Check if PostgreSQL is installed and running"""
    print("🔍 Checking PostgreSQL status...")
    
    # Check if PostgreSQL is installed
    result = subprocess.run("which psql", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ PostgreSQL is not installed. Please install it first:")
        print("   sudo pacman -S postgresql")
        return False
    
    # Check if PostgreSQL service is running
    result = subprocess.run("sudo systemctl is-active postgresql", shell=True, capture_output=True, text=True)
    if result.stdout.strip() != "active":
        print("🔧 PostgreSQL service is not running. Starting it...")
        start_result = run_command("sudo systemctl start postgresql", "Starting PostgreSQL service")
        if start_result is None:
            return False
        
        # Enable PostgreSQL to start on boot
        run_command("sudo systemctl enable postgresql", "Enabling PostgreSQL on boot")
    
    print("✅ PostgreSQL is installed and running")
    return True

def create_database_and_user():
    """Create database and user for Phantom Banking"""
    print("🏗️  Creating database and user...")
    
    # Database configuration from environment
    db_name = env('DB_NAME', default='phantom_banking_dev')
    db_user = env('DB_USER', default='phantom_dev')
    db_password = env('DB_PASSWORD', default='phantom123')
    
    try:
        # Connect to PostgreSQL as postgres user
        print("🔌 Connecting to PostgreSQL as postgres user...")
        
        # Try to connect as postgres user
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='postgres',
                user='postgres'
            )
        except psycopg2.OperationalError:
            print("⚠️  Cannot connect as postgres user. Trying with sudo...")
            # Create the database using sudo and psql commands
            create_db_sql = f"""
            CREATE USER {db_user} WITH PASSWORD '{db_password}';
            CREATE DATABASE {db_name} OWNER {db_user};
            GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};
            ALTER USER {db_user} CREATEDB;
            """
            
            # Write SQL to temporary file
            sql_file = project_root / 'temp_db_setup.sql'
            with open(sql_file, 'w') as f:
                f.write(create_db_sql)
            
            # Execute SQL file as postgres user
            result = run_command(
                f"sudo -u postgres psql -f {sql_file}",
                f"Creating database {db_name} and user {db_user}"
            )
            
            # Clean up temporary file
            sql_file.unlink()
            
            if result is not None:
                print(f"✅ Database '{db_name}' and user '{db_user}' created successfully")
                return True
            else:
                return False
        
        # If direct connection worked, use it
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_user WHERE usename = %s", (db_user,))
        user_exists = cursor.fetchone() is not None
        
        if not user_exists:
            print(f"👤 Creating user '{db_user}'...")
            cursor.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
            cursor.execute(f"ALTER USER {db_user} CREATEDB")
            print(f"✅ User '{db_user}' created")
        else:
            print(f"👤 User '{db_user}' already exists")
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        db_exists = cursor.fetchone() is not None
        
        if not db_exists:
            print(f"🗄️  Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user}")
            print(f"✅ Database '{db_name}' created")
        else:
            print(f"🗄️  Database '{db_name}' already exists")
        
        # Grant privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        print(f"✅ Privileges granted to user '{db_user}'")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_database_connection():
    """Test connection to the created database"""
    print("🧪 Testing database connection...")
    
    db_name = env('DB_NAME', default='phantom_banking_dev')
    db_user = env('DB_USER', default='phantom_dev')
    db_password = env('DB_PASSWORD', default='phantom123')
    db_host = env('DB_HOST', default='localhost')
    db_port = env('DB_PORT', default='5432')
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection successful!")
        print(f"   PostgreSQL version: {version}")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        return False

def setup_redis():
    """Check and setup Redis"""
    print("🔍 Checking Redis...")
    
    # Check if Redis is installed
    result = subprocess.run("which redis-server", shell=True, capture_output=True)
    if result.returncode != 0:
        print("⚠️  Redis is not installed. Installing...")
        install_result = run_command("sudo pacman -S redis", "Installing Redis")
        if install_result is None:
            print("❌ Failed to install Redis. Please install manually: sudo pacman -S redis")
            return False
    
    # Check if Redis service is running
    result = subprocess.run("sudo systemctl is-active redis", shell=True, capture_output=True, text=True)
    if result.stdout.strip() != "active":
        print("🔧 Redis service is not running. Starting it...")
        start_result = run_command("sudo systemctl start redis", "Starting Redis service")
        if start_result is None:
            return False
        
        # Enable Redis to start on boot
        run_command("sudo systemctl enable redis", "Enabling Redis on boot")
    
    print("✅ Redis is installed and running")
    return True

def main():
    """Main setup function"""
    print("🏦 Phantom Banking - PostgreSQL Database Setup")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = project_root / '.env'
    if not env_file.exists():
        print("❌ .env file not found. Please copy .env.example to .env first:")
        print("   cp .env.example .env")
        sys.exit(1)
    
    print(f"📂 Project root: {project_root}")
    print(f"🗂️  Environment file: {env_file}")
    
    # Step 1: Check PostgreSQL
    if not check_postgresql_status():
        print("❌ PostgreSQL setup failed. Please install and start PostgreSQL manually.")
        sys.exit(1)
    
    # Step 2: Create database and user
    if not create_database_and_user():
        print("❌ Database creation failed.")
        sys.exit(1)
    
    # Step 3: Test database connection
    if not test_database_connection():
        print("❌ Database connection test failed.")
        sys.exit(1)
    
    # Step 4: Setup Redis
    if not setup_redis():
        print("⚠️  Redis setup failed, but you can continue without it for now.")
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Install Python dependencies: pip install -r requirements.txt")
    print("2. Run migrations: python manage.py migrate")
    print("3. Test migrations: python scripts/test_migrations.py")
    print("4. Create superuser: python manage.py createsuperuser")
    print("5. Run development server: python manage.py runserver")
    print("\n✅ Your Phantom Banking backend is ready for development!")

if __name__ == "__main__":
    main()
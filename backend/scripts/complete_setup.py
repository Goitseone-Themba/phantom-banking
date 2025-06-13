import os
import sys
import subprocess
import time
from pathlib import Path

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
            cwd=cwd
        )
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def check_python_version():
    """Check Python version compatibility for Django 5.2+"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or version.minor < 10:
        print("❌ Python 3.10+ is required for Django 5.2+")
        print(f"   Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor} (Django 5.2+ compatible)")
    return True

def check_system_dependencies():
    """Check if system dependencies are available"""
    print("🔍 Checking system dependencies...")
    
    dependencies = {
        'PostgreSQL': 'psql --version',
        'Redis': 'redis-server --version',
        'Git': 'git --version',
    }
    
    all_available = True
    for name, command in dependencies.items():
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"   ✅ {name}: {version}")
            else:
                print(f"   ❌ {name}: Not available")
                all_available = False
        except:
            print(f"   ❌ {name}: Not available")
            all_available = False
    
    return all_available

def main():
    """Complete setup process"""
    print("🏦 Phantom Banking - Complete PostgreSQL Setup (Django 5.2+ Compatible)")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent
    print(f"📂 Project root: {project_root}")
    
    # Step 1: Check Python version
    if not check_python_version():
        print("💡 Install Python 3.10+ with: sudo pacman -S python")
        return False
    
    # Step 2: Check system dependencies
    if not check_system_dependencies():
        print("💡 Install missing dependencies:")
        print("   sudo pacman -S postgresql redis git")
        return False
    
    # Step 3: Create project structure
    print("\n📁 Creating project structure...")
    if not run_command("python generate_project_structure.py", "Generating project structure", project_root):
        return False
    
    # Step 4: Setup PostgreSQL database
    print("\n🗄️  Setting up PostgreSQL database...")
    if not run_command("python scripts/setup_database.py", "Setting up database", project_root):
        return False
    
    # Step 5: Install Python dependencies
    print("\n📦 Installing Python dependencies (Django 5.2+ compatible)...")
    if not run_command("pip install --upgrade pip", "Upgrading pip", project_root):
        return False
    
    if not run_command("pip install -r requirements.txt", "Installing dependencies", project_root):
        return False
    
    # Step 6: Run migrations
    print("\n🔄 Running Django migrations...")
    if not run_command("python manage.py makemigrations", "Making migrations", project_root):
        return False
    
    if not run_command("python manage.py migrate", "Applying migrations", project_root):
        return False
    
    # Step 7: Test everything
    print("\n🧪 Running comprehensive tests...")
    if not run_command("python scripts/test_migrations.py", "Testing setup", project_root):
        return False
    
    # Step 8: Collect static files (Django 5.2+ with WhiteNoise)
    print("\n📁 Collecting static files...")
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files", project_root):
        print("⚠️  Static files collection failed, but continuing...")
    
    # Step 9: Create superuser (optional)
    print("\n👤 Creating superuser (optional)...")
    print("   You can create a superuser later with: python manage.py createsuperuser")
    
    print("\n🎉 Complete setup finished successfully!")
    print("\n📋 Next steps:")
    print("1. Create superuser: python manage.py createsuperuser")
    print("2. Start development server: python scripts/dev_server.py")
    print("3. Visit admin: http://localhost:8000/admin/")
    print("4. Test API: http://localhost:8000/api/v1/health/")
    print("5. View API docs: http://localhost:8000/api/docs/")
    print("\n🚀 Ready for Django 5.2+ development for FNB Hackathon 2025!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
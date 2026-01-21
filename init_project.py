#!/usr/bin/env python
"""
Quick initialization script for the Events Platform.
This script will:
1. Check if virtual environment exists
2. Install dependencies
3. Setup database
4. Run migrations
5. Optionally create superuser

Usage:
    python init_project.py
"""

import os
import sys
import subprocess
import platform


def run_command(command, description, shell=True):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        print(f"Current version: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")


def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("\n⚠️  .env file not found!")
        print("Creating .env from .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file")
            print("⚠️  Please update .env with your configuration!")
        else:
            print("❌ .env.example not found")
            sys.exit(1)
    else:
        print("✅ .env file exists")


def main():
    """Main initialization function"""
    print("\n" + "="*60)
    print("🚀 Events Platform - Initialization Script")
    print("="*60)
    
    # Check Python version
    check_python_version()
    
    # Check environment file
    check_env_file()
    
    # Detect OS
    is_windows = platform.system() == 'Windows'
    python_cmd = 'python' if is_windows else 'python3'
    
    print("\n📋 Setup Steps:")
    print("1. Create virtual environment")
    print("2. Install dependencies")
    print("3. Run database migrations")
    print("4. Setup periodic tasks (optional)")
    print("5. Create superuser (optional)")
    
    response = input("\n❓ Continue with setup? (y/n): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        sys.exit(0)
    
    # Step 1: Check/Create virtual environment
    venv_exists = os.path.exists('venv') or os.path.exists('.venv')
    if not venv_exists:
        print("\n⚠️  Virtual environment not found.")
        create_venv = input("❓ Create virtual environment? (y/n): ")
        if create_venv.lower() == 'y':
            run_command(
                f'{python_cmd} -m venv venv',
                'Creating virtual environment'
            )
    else:
        print("✅ Virtual environment exists")
    
    # Step 2: Install dependencies
    print("\n⚠️  Installing dependencies...")
    print("This may take a few minutes...")
    
    if is_windows:
        pip_cmd = 'venv\\Scripts\\pip.exe'
        python_venv = 'venv\\Scripts\\python.exe'
    else:
        pip_cmd = 'venv/bin/pip'
        python_venv = 'venv/bin/python'
    
    if os.path.exists(pip_cmd):
        run_command(
            f'{pip_cmd} install --upgrade pip',
            'Upgrading pip'
        )
        run_command(
            f'{pip_cmd} install -r requirements.txt',
            'Installing dependencies'
        )
    else:
        print("⚠️  Using system Python")
        run_command(
            f'{python_cmd} -m pip install -r requirements.txt',
            'Installing dependencies'
        )
        python_venv = python_cmd
    
    # Step 3: Run migrations
    print("\n⚠️  Database Setup")
    print("Make sure PostgreSQL is running and credentials in .env are correct")
    
    response = input("❓ Run database migrations? (y/n): ")
    if response.lower() == 'y':
        run_command(
            f'{python_venv} manage.py makemigrations',
            'Creating migrations'
        )
        run_command(
            f'{python_venv} manage.py migrate',
            'Running migrations'
        )
    
    # Step 4: Setup periodic tasks
    response = input("\n❓ Setup Celery periodic tasks for emails? (y/n): ")
    if response.lower() == 'y':
        run_command(
            f'{python_venv} setup_tasks.py',
            'Setting up periodic tasks'
        )
    
    # Step 5: Create superuser
    response = input("\n❓ Create Django superuser? (y/n): ")
    if response.lower() == 'y':
        print("\n📝 Creating superuser...")
        print("You'll be prompted for credentials:")
        os.system(f'{python_venv} manage.py createsuperuser')
    
    # Final instructions
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\n📚 Next Steps:")
    print("\n1. Activate virtual environment:")
    if is_windows:
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Start the development server:")
    print("   python manage.py runserver")
    
    print("\n3. (Optional) Start Celery for scheduled emails:")
    print("   Terminal 1: celery -A events_platform worker -l info")
    print("   Terminal 2: celery -A events_platform beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler")
    
    print("\n4. Access the application:")
    print("   API: http://localhost:8000")
    print("   Admin: http://localhost:8000/admin")
    print("   Docs: http://localhost:8000/api/docs/")
    
    print("\n5. Import Postman collection:")
    print("   postman_collection.json")
    
    print("\n📖 Documentation:")
    print("   - README.md - Full documentation")
    print("   - QUICKSTART.md - Quick start guide")
    print("   - DEPLOYMENT.md - Deployment guide")
    print("   - PROJECT_SUMMARY.md - Project overview")
    
    print("\n🎉 Happy Coding!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()

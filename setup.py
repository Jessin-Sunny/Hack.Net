#!/usr/bin/env python3
"""
Setup script for Venue Booking System
This script helps set up the environment and run the application.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        return False

def create_upload_folder():
    """Create uploads folder if it doesn't exist"""
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print("✅ Created uploads folder")
    else:
        print("✅ Uploads folder already exists")

def run_application():
    """Run the Flask application"""
    print("🚀 Starting Venue Booking System...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("👤 Default admin account: admin / admin123")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main setup function"""
    print("🏢 Venue Booking System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create upload folder
    create_upload_folder()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Quick Start Guide:")
    print("1. The application will start automatically")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Login as admin (admin/admin123) or register new accounts")
    print("4. Start managing venue bookings!")
    
    # Run the application
    run_application()

if __name__ == "__main__":
    main() 
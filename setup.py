#!/usr/bin/env python3
"""
Quick setup script for AskPOTATO
Automates the initial project setup
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def check_python_version():
    """Check if Python version is 3.8+"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher required")
        return False
    
    print("✅ Python version OK")
    return True


def create_virtualenv():
    """Create virtual environment"""
    print_header("Creating Virtual Environment")
    
    if Path("venv").exists():
        print("Virtual environment already exists")
        response = input("Recreate? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing venv")
            return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False


def get_pip_command():
    """Get the correct pip command for the platform"""
    if sys.platform == "win32":
        return "venv\\Scripts\\pip.exe"
    return "venv/bin/pip"


def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    pip_cmd = get_pip_command()
    
    try:
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def create_env_file():
    """Create .env file from template"""
    print_header("Creating Environment File")
    
    if Path(".env").exists():
        print(".env file already exists")
        return True
    
    if Path(".env.example").exists():
        import shutil
        shutil.copy(".env.example", ".env")
        print("✅ Created .env from template")
        print("⚠️  Remember to update SECRET_KEY in .env!")
        return True
    else:
        print("⚠️  .env.example not found, skipping")
        return True


def create_uploads_folder():
    """Create uploads folder"""
    print_header("Creating Upload Folder")
    
    Path("uploads").mkdir(exist_ok=True)
    print("✅ Upload folder created")
    return True


def initialize_database():
    """Initialize the database"""
    print_header("Database Initialization")
    
    if Path("potato.db").exists():
        print("Database already exists")
        response = input("Reinitialize? This will delete existing data (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing database")
            return True
    
    try:
        python_cmd = "venv\\Scripts\\python.exe" if sys.platform == "win32" else "venv/bin/python"
        subprocess.run([python_cmd, "init_db.py"], check=True)
        print("✅ Database initialized")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to initialize database")
        return False


def check_ollama():
    """Check if Ollama is installed"""
    print_header("Checking Ollama")
    
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            
            # Check if llama3 model is available
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if "llama3" in result.stdout:
                print("✅ llama3 model is available")
            else:
                print("⚠️  llama3 model not found")
                print("   Run: ollama pull llama3")
            return True
    except FileNotFoundError:
        print("⚠️  Ollama not found")
        print("   Install from: https://ollama.ai/")
        print("   Then run: ollama pull llama3")
        return False


def main():
    """Main setup function"""
    print_header("🥔 AskPOTATO Setup Script")
    
    steps = [
        ("Python Version", check_python_version),
        ("Virtual Environment", create_virtualenv),
        ("Dependencies", install_dependencies),
        ("Environment File", create_env_file),
        ("Upload Folder", create_uploads_folder),
        ("Database", initialize_database),
        ("Ollama", check_ollama)
    ]
    
    results = []
    for name, func in steps:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Setup Summary")
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print_header("🎉 Setup Complete!")
        print("\nNext steps:")
        print("1. Activate virtual environment:")
        if sys.platform == "win32":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("\n2. Start the application:")
        print("   python app.py")
        print("\n3. Open browser:")
        print("   http://localhost:5000")
        return 0
    else:
        print_header("⚠️  Setup Incomplete")
        print("\nSome steps failed. Please review the errors above.")
        print("You can run individual steps manually:")
        print("- pip install -r requirements.txt")
        print("- python init_db.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())

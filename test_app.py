#!/usr/bin/env python3
"""
Simple test script to verify the application works
Run: python test_app.py
"""

import sys
import sqlite3
from pathlib import Path


def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import flask
        import requests
        import werkzeug
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def test_database():
    """Test if database exists and has correct schema"""
    print("\nTesting database...")
    db_path = Path("potato.db")
    
    if not db_path.exists():
        print("✗ Database not found. Run: python init_db.py")
        return False
    
    try:
        conn = sqlite3.connect("potato.db")
        cur = conn.cursor()
        
        # check tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        required_tables = ['scenarios', 'steps', 'defects', 'proofs']
        
        for table in required_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' missing")
                return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_config():
    """Test if config can be loaded"""
    print("\nTesting configuration...")
    try:
        from config import Config
        print(f"✓ Config loaded")
        print(f"  - Database: {Config.DATABASE}")
        print(f"  - Upload folder: {Config.UPLOAD_FOLDER}")
        print(f"  - Ollama URL: {Config.OLLAMA_URL}")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False


def test_askpotato_module():
    """Test if askpotato module works"""
    print("\nTesting askpotato module...")
    try:
        from askpotato.intents import INTENTS
        from askpotato.detector import detect_intent
        
        print(f"✓ Module loaded successfully")
        print(f"  - Supported intents: {len(INTENTS)}")
        
        # test intent detection
        test_intent = detect_intent("LIST_SCENARIOS")
        if test_intent == "LIST_SCENARIOS":
            print("✓ Intent detection works")
        else:
            print("✗ Intent detection failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Module error: {e}")
        return False


def test_app_creation():
    """Test if Flask app can be created"""
    print("\nTesting Flask app creation...")
    try:
        from app import app
        print("✓ Flask app created successfully")
        print(f"  - Debug mode: {app.config['DEBUG']}")
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AskPOTATO - Application Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Configuration", test_config),
        ("AskPOTATO Module", test_askpotato_module),
        ("Flask App", test_app_creation)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n All tests passed! You can run the app with: python app.py")
        return 0
    else:
        print("\n Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

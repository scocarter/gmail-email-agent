#!/usr/bin/env python3
"""
Gmail API Setup Verification Script
"""

import os
import json
import sys
from pathlib import Path

def check_credentials_file():
    """Check if credentials.json exists and is valid"""
    cred_path = Path("config/credentials.json")
    
    if not cred_path.exists():
        print("❌ config/credentials.json not found")
        print("   Run: ./setup_gmail_api.sh")
        return False
    
    try:
        with open(cred_path) as f:
            data = json.load(f)
        
        # Check if it has the required structure
        if "installed" not in data:
            print("❌ Invalid credentials file format")
            return False
        
        required_fields = ["client_id", "client_secret", "auth_uri", "token_uri"]
        installed = data["installed"]
        
        for field in required_fields:
            if field not in installed:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ Credentials file is valid")
        
        # Show project info
        project_id = installed.get("project_id", "Unknown")
        client_id = installed.get("client_id", "Unknown")
        print(f"   Project ID: {project_id}")
        print(f"   Client ID: {client_id[:20]}...")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in credentials file")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False

def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "google-api-python-client",
        "google-auth-httplib2", 
        "google-auth-oauthlib",
        "google-auth"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is NOT installed")
    
    if missing_packages:
        print("\n🔧 To install missing packages, run:")
        print("   pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_configuration():
    """Check if config.yaml is properly configured"""
    config_path = Path("config/config.yaml")
    
    if not config_path.exists():
        print("❌ config/config.yaml not found")
        return False
    
    try:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check Gmail configuration
        gmail_config = config.get("gmail", {})
        expected_files = ["config/credentials.json", "config/token.json"]
        
        cred_file = gmail_config.get("credentials_file", "")
        if cred_file != "config/credentials.json":
            print(f"⚠️  Credentials file path should be 'config/credentials.json', found: {cred_file}")
        
        print("✅ Configuration file is valid")
        return True
        
    except ImportError:
        print("❌ PyYAML not installed. Run: pip install PyYAML")
        return False
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Gmail Email Agent Setup Verification")
    print("=" * 40)
    
    checks = [
        ("Python Dependencies", check_python_dependencies),
        ("Gmail API Credentials", check_credentials_file),
        ("Configuration File", check_configuration),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\n📝 Next steps:")
        print("1. Run: python src/cli.py test")
        print("2. This will test Gmail authentication")
        print("3. If successful, try: python src/cli.py listen")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

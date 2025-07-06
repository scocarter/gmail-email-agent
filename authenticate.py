#!/usr/bin/env python3
"""
Simple Gmail API Authentication Script
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

def authenticate_gmail():
    """Authenticate with Gmail API"""
    creds = None
    
    # Check if token already exists
    if os.path.exists('config/token.json'):
        creds = Credentials.from_authorized_user_file('config/token.json', SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting Gmail authentication...")
            print("This will open your browser for authentication.")
            print("Please sign in and grant permissions to the Gmail Email Agent.")
            print("")
            
            # Start OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save credentials for next time
        with open('config/token.json', 'w') as token:
            token.write(creds.to_json())
        print("✅ Credentials saved successfully!")
    
    return creds

def test_gmail_connection(creds):
    """Test Gmail API connection"""
    try:
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Test connection
        profile = service.users().getProfile(userId='me').execute()
        
        print("🎉 Gmail API connection successful!")
        print(f"📧 Connected to: {profile['emailAddress']}")
        print(f"📊 Total messages: {profile.get('messagesTotal', 'Unknown')}")
        print(f"📊 Total threads: {profile.get('threadsTotal', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gmail API connection failed: {e}")
        return False

def main():
    """Main authentication function"""
    print("🚀 Gmail Email Agent - Authentication Setup")
    print("=" * 50)
    
    # Check if credentials file exists
    if not os.path.exists('config/credentials.json'):
        print("❌ credentials.json not found in config/ directory")
        print("Please run ./setup_gmail_api.sh first")
        sys.exit(1)
    
    try:
        # Authenticate
        creds = authenticate_gmail()
        
        # Test connection
        if test_gmail_connection(creds):
            print("\n🎊 Setup Complete!")
            print("You can now run the email agent:")
            print("  python src/cli.py listen    # Start monitoring")
            print("  python src/cli.py batch     # Process past emails")
            print("  python src/cli.py junk      # Find junk emails")
        else:
            print("\n❌ Setup failed. Please check your configuration.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Authentication cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")

if __name__ == "__main__":
    main()

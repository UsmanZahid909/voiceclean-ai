#!/usr/bin/env python3
"""
VoiceClean AI - Google OAuth Setup Helper
This script helps you configure Google OAuth for your SaaS application.
"""

import os
import secrets
from dotenv import load_dotenv, set_key

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def setup_oauth():
    """Interactive setup for Google OAuth"""
    print("🚀 VoiceClean AI - Google OAuth Setup")
    print("=" * 50)
    
    # Load existing .env
    load_dotenv()
    
    print("\n📋 Current Configuration:")
    print(f"GOOGLE_CLIENT_ID: {os.getenv('GOOGLE_CLIENT_ID', 'Not set')}")
    print(f"GOOGLE_CLIENT_SECRET: {'Set' if os.getenv('GOOGLE_CLIENT_SECRET') else 'Not set'}")
    print(f"FLASK_SECRET_KEY: {'Set' if os.getenv('FLASK_SECRET_KEY') else 'Not set'}")
    
    print("\n🔧 Setup Options:")
    print("1. Configure Google OAuth credentials")
    print("2. Generate new Flask secret key")
    print("3. View setup instructions")
    print("4. Test current configuration")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        configure_google_oauth()
    elif choice == "2":
        generate_flask_secret()
    elif choice == "3":
        show_instructions()
    elif choice == "4":
        test_configuration()
    elif choice == "5":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid option. Please try again.")
        setup_oauth()

def configure_google_oauth():
    """Configure Google OAuth credentials"""
    print("\n🔐 Google OAuth Configuration")
    print("-" * 30)
    
    print("\n📝 Please enter your Google OAuth credentials:")
    print("(Get these from: https://console.cloud.google.com)")
    
    client_id = input("\nGoogle Client ID: ").strip()
    client_secret = input("Google Client Secret: ").strip()
    
    if client_id and client_secret:
        # Update .env file
        set_key('.env', 'GOOGLE_CLIENT_ID', client_id)
        set_key('.env', 'GOOGLE_CLIENT_SECRET', client_secret)
        
        print("\n✅ Google OAuth credentials saved!")
        print("🔄 Please restart your application to apply changes.")
        
        # Also generate secret key if not set
        if not os.getenv('FLASK_SECRET_KEY') or os.getenv('FLASK_SECRET_KEY') == 'your-super-secret-key-change-this-in-production':
            print("\n🔑 Generating secure Flask secret key...")
            secret_key = generate_secret_key()
            set_key('.env', 'FLASK_SECRET_KEY', secret_key)
            print("✅ Flask secret key generated!")
    else:
        print("❌ Please provide both Client ID and Client Secret.")
    
    input("\nPress Enter to continue...")
    setup_oauth()

def generate_flask_secret():
    """Generate a new Flask secret key"""
    print("\n🔑 Generating Flask Secret Key")
    print("-" * 30)
    
    secret_key = generate_secret_key()
    set_key('.env', 'FLASK_SECRET_KEY', secret_key)
    
    print(f"✅ New secret key generated: {secret_key[:20]}...")
    print("🔄 Please restart your application to apply changes.")
    
    input("\nPress Enter to continue...")
    setup_oauth()

def show_instructions():
    """Show setup instructions"""
    print("\n📖 Google OAuth Setup Instructions")
    print("=" * 40)
    
    instructions = """
1. Go to Google Cloud Console: https://console.cloud.google.com
2. Create a new project: "VoiceClean AI"
3. Enable Google+ API
4. Configure OAuth consent screen:
   - App name: VoiceClean AI
   - Add your email as test user
5. Create OAuth 2.0 credentials:
   - Type: Web application
   - Authorized redirect URIs:
     * http://localhost:3000/auth/callback
     * http://localhost:5000/auth/callback
     * http://localhost:8000/auth/callback
6. Copy Client ID and Client Secret
7. Run this setup script and enter credentials
8. Restart your application

For detailed instructions, see: GOOGLE_OAUTH_SETUP.md
"""
    
    print(instructions)
    input("\nPress Enter to continue...")
    setup_oauth()

def test_configuration():
    """Test current OAuth configuration"""
    print("\n🧪 Testing Configuration")
    print("-" * 25)
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    secret_key = os.getenv('FLASK_SECRET_KEY')
    
    print("Checking configuration...")
    
    # Check Google Client ID
    if client_id and client_id != 'your-google-client-id.apps.googleusercontent.com':
        if client_id.endswith('.apps.googleusercontent.com'):
            print("✅ Google Client ID: Valid format")
        else:
            print("⚠️  Google Client ID: Invalid format")
    else:
        print("❌ Google Client ID: Not configured")
    
    # Check Google Client Secret
    if client_secret and client_secret != 'your-google-client-secret':
        if client_secret.startswith('GOCSPX-'):
            print("✅ Google Client Secret: Valid format")
        else:
            print("⚠️  Google Client Secret: Unusual format")
    else:
        print("❌ Google Client Secret: Not configured")
    
    # Check Flask Secret Key
    if secret_key and secret_key != 'your-super-secret-key-change-this-in-production':
        if len(secret_key) >= 32:
            print("✅ Flask Secret Key: Secure length")
        else:
            print("⚠️  Flask Secret Key: Too short")
    else:
        print("❌ Flask Secret Key: Using default (insecure)")
    
    # Overall status
    if all([client_id, client_secret, secret_key]) and \
       client_id != 'your-google-client-id.apps.googleusercontent.com' and \
       client_secret != 'your-google-client-secret':
        print("\n🎉 Configuration looks good!")
        print("🔄 Restart your app to enable Google OAuth")
    else:
        print("\n⚠️  Configuration incomplete")
        print("📝 Please configure missing credentials")
    
    input("\nPress Enter to continue...")
    setup_oauth()

if __name__ == "__main__":
    try:
        setup_oauth()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your configuration and try again.")
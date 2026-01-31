#!/usr/bin/env python3
"""
Enable Firebase Services for VoiceClean AI
"""

def enable_firebase_services():
    print("🔥 Firebase Services Setup for VoiceClean AI")
    print("=" * 50)
    
    print(f"\n📋 Your Firebase Project Details:")
    print(f"Project ID: avian-mystery-433509-u5")
    print(f"API Key: AIzaSyAB3EfEbhUDMB4ZYk6pFTQ6Vl6EC1Sa2fI")
    print(f"Auth Domain: avian-mystery-433509-u5.firebaseapp.com")
    
    print(f"\n🔧 STEP 1: Enable Authentication")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/authentication")
    print("2. Click 'Get started'")
    print("3. Go to 'Sign-in method' tab")
    print("4. Enable 'Email/Password':")
    print("   - Click on 'Email/Password'")
    print("   - Toggle 'Enable'")
    print("   - Click 'Save'")
    print("5. Enable 'Google':")
    print("   - Click on 'Google'")
    print("   - Toggle 'Enable'")
    print("   - Select your project support email")
    print("   - Click 'Save'")
    
    print(f"\n🗄️ STEP 2: Enable Firestore Database")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/firestore")
    print("2. Click 'Create database'")
    print("3. Choose 'Start in test mode'")
    print("4. Select location: 'us-central1' (recommended)")
    print("5. Click 'Done'")
    
    print(f"\n🌐 STEP 3: Add Authorized Domains")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/authentication/settings")
    print("2. Scroll to 'Authorized domains'")
    print("3. Click 'Add domain'")
    print("4. Add: voiceclean-ai.vercel.app")
    print("5. Add: localhost (for testing)")
    
    print(f"\n🔐 STEP 4: Set up Firestore Security Rules")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/firestore/rules")
    print("2. Replace the rules with:")
    print("""
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
    """)
    print("3. Click 'Publish'")
    
    print(f"\n✅ After completing these steps:")
    print("1. Your Firebase project will be ready")
    print("2. Users can sign up with email/password or Google")
    print("3. User data will be stored in Firestore")
    print("4. Usage limits will be tracked per user")
    
    print(f"\n🚀 Ready to deploy with full Firebase integration!")

if __name__ == "__main__":
    enable_firebase_services()
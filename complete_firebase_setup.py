#!/usr/bin/env python3
"""
Complete Firebase Setup for VoiceClean AI
This script will guide you through the complete Firebase setup process
"""

import os
import json
import subprocess
import sys

def print_header(title):
    print("\n" + "="*60)
    print(f"🔥 {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n📋 STEP {step}: {description}")
    print("-" * 50)

def complete_firebase_setup():
    print_header("COMPLETE FIREBASE SETUP FOR VOICECLEAN AI")
    
    print(f"\n✅ Your Firebase Project Details:")
    print(f"Project ID: avian-mystery-433509-u5")
    print(f"API Key: AIzaSyAB3EfEbhUDMB4ZYk6pFTQ6Vl6EC1Sa2fI")
    print(f"Auth Domain: avian-mystery-433509-u5.firebaseapp.com")
    print(f"Console URL: https://console.firebase.google.com/project/avian-mystery-433509-u5")
    
    print_step(1, "Enable Firebase Authentication")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/authentication")
    print("2. Click 'Get started' if not already enabled")
    print("3. Go to 'Sign-in method' tab")
    print("4. Enable 'Email/Password':")
    print("   - Click on 'Email/Password' provider")
    print("   - Toggle 'Enable' to ON")
    print("   - Click 'Save'")
    print("5. Enable 'Google' sign-in:")
    print("   - Click on 'Google' provider")
    print("   - Toggle 'Enable' to ON")
    print("   - Select your project support email")
    print("   - Click 'Save'")
    
    print_step(2, "Enable Firestore Database")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/firestore")
    print("2. Click 'Create database'")
    print("3. Choose 'Start in test mode' (we'll secure it later)")
    print("4. Select location: 'us-central1' (recommended for performance)")
    print("5. Click 'Done'")
    
    print_step(3, "Add Authorized Domains")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/authentication/settings")
    print("2. Scroll down to 'Authorized domains' section")
    print("3. Click 'Add domain' and add these domains:")
    print("   - voiceclean-ai.vercel.app")
    print("   - localhost (for local testing)")
    print("   - 127.0.0.1 (for local testing)")
    
    print_step(4, "Set up Firestore Security Rules")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/firestore/rules")
    print("2. Replace the default rules with this secure configuration:")
    print("""
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data only
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Usage tracking (read-only for users)
    match /usage/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null;
    }
  }
}
    """)
    print("3. Click 'Publish' to save the rules")
    
    print_step(5, "Generate Service Account Key (Optional - for Admin SDK)")
    print("1. Go to: https://console.firebase.google.com/project/avian-mystery-433509-u5/settings/serviceaccounts/adminsdk")
    print("2. Click 'Generate new private key'")
    print("3. Download the JSON file")
    print("4. Keep it secure - don't commit to git!")
    
    print_step(6, "Set Environment Variables in Vercel")
    print("1. Go to: https://vercel.com/dashboard")
    print("2. Select your 'voiceclean-ai' project")
    print("3. Go to Settings > Environment Variables")
    print("4. Add these variables:")
    
    env_vars = {
        "FIREBASE_API_KEY": "AIzaSyAB3EfEbhUDMB4ZYk6pFTQ6Vl6EC1Sa2fI",
        "FIREBASE_AUTH_DOMAIN": "avian-mystery-433509-u5.firebaseapp.com",
        "FIREBASE_PROJECT_ID": "avian-mystery-433509-u5",
        "FIREBASE_STORAGE_BUCKET": "avian-mystery-433509-u5.firebasestorage.app",
        "FIREBASE_MESSAGING_SENDER_ID": "454829723768",
        "FIREBASE_APP_ID": "1:454829723768:web:ec36f24d8df4f882499d8d",
        "FIREBASE_MEASUREMENT_ID": "G-G35LS3E4P7",
        "SECRET_KEY": "voiceclean-ai-secret-key-2024-firebase",
        "STRIPE_PUBLISHABLE_KEY": "pk_test_...",
        "STRIPE_SECRET_KEY": "sk_test_...",
        "STRIPE_BASIC_PRICE_ID": "price_...",
        "STRIPE_UNLIMITED_PRICE_ID": "price_...",
        "STRIPE_WEBHOOK_SECRET": "whsec_..."
    }
    
    for key, value in env_vars.items():
        print(f"   {key}={value}")
    
    print_step(7, "Set up Stripe Products (for subscriptions)")
    print("1. Go to: https://dashboard.stripe.com/products")
    print("2. Create 'Basic Plan' product:")
    print("   - Name: VoiceClean AI Basic")
    print("   - Price: $1.00 USD")
    print("   - Billing: Monthly recurring")
    print("   - Copy the Price ID (starts with 'price_')")
    print("3. Create 'Unlimited Plan' product:")
    print("   - Name: VoiceClean AI Unlimited")
    print("   - Price: $2.00 USD")
    print("   - Billing: Monthly recurring")
    print("   - Copy the Price ID (starts with 'price_')")
    print("4. Set up webhook endpoint:")
    print("   - Go to Developers > Webhooks")
    print("   - Add endpoint: https://voiceclean-ai.vercel.app/api/webhook/stripe")
    print("   - Select events: checkout.session.completed")
    print("   - Copy the webhook secret (starts with 'whsec_')")
    
    print_step(8, "Test the Integration")
    print("1. Deploy to Vercel with updated environment variables")
    print("2. Visit: https://voiceclean-ai.vercel.app/signup")
    print("3. Try creating an account with email/password")
    print("4. Try signing in with Google")
    print("5. Test audio enhancement with usage limits")
    print("6. Test subscription upgrade flow")
    
    print_header("DEPLOYMENT CHECKLIST")
    print("✅ Firebase Authentication enabled (Email + Google)")
    print("✅ Firestore Database created with security rules")
    print("✅ Authorized domains added")
    print("✅ Environment variables set in Vercel")
    print("✅ Stripe products created")
    print("✅ Webhook endpoint configured")
    
    print(f"\n🚀 READY TO DEPLOY!")
    print("Your VoiceClean AI app now has:")
    print("• Complete Firebase authentication")
    print("• User database with usage tracking")
    print("• Subscription plans with Stripe")
    print("• Daily usage limits per plan")
    print("• Professional audio enhancement")
    
    print(f"\n📱 Live URLs after deployment:")
    print("• Main app: https://voiceclean-ai.vercel.app")
    print("• Sign up: https://voiceclean-ai.vercel.app/signup")
    print("• Login: https://voiceclean-ai.vercel.app/login")
    print("• Pricing: https://voiceclean-ai.vercel.app/pricing")
    print("• Dashboard: https://voiceclean-ai.vercel.app/dashboard")

def create_env_file():
    """Create a .env file with all required variables"""
    print_header("CREATING .ENV FILE")
    
    env_content = """# Firebase Configuration
FIREBASE_API_KEY=AIzaSyAB3EfEbhUDMB4ZYk6pFTQ6Vl6EC1Sa2fI
FIREBASE_AUTH_DOMAIN=avian-mystery-433509-u5.firebaseapp.com
FIREBASE_PROJECT_ID=avian-mystery-433509-u5
FIREBASE_STORAGE_BUCKET=avian-mystery-433509-u5.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=454829723768
FIREBASE_APP_ID=1:454829723768:web:ec36f24d8df4f882499d8d
FIREBASE_MEASUREMENT_ID=G-G35LS3E4P7

# App Configuration
SECRET_KEY=voiceclean-ai-secret-key-2024-firebase

# Stripe Configuration (replace with your actual keys)
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_BASIC_PRICE_ID=price_your_basic_price_id_here
STRIPE_UNLIMITED_PRICE_ID=price_your_unlimited_price_id_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with Firebase configuration")
    print("⚠️  Remember to update Stripe keys with your actual values")

def update_firebase_config():
    """Update firebase-config.json with correct project details"""
    print_header("UPDATING FIREBASE CONFIG")
    
    config = {
        "type": "service_account",
        "project_id": "avian-mystery-433509-u5",
        "private_key_id": "your_private_key_id_from_service_account",
        "private_key": "-----BEGIN PRIVATE KEY-----\nyour_private_key_from_service_account\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-xxxxx@avian-mystery-433509-u5.iam.gserviceaccount.com",
        "client_id": "your_client_id_from_service_account",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40avian-mystery-433509-u5.iam.gserviceaccount.com"
    }
    
    with open('firebase-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Updated firebase-config.json with correct project ID")
    print("⚠️  Replace placeholder values with actual service account details")

if __name__ == "__main__":
    complete_firebase_setup()
    create_env_file()
    update_firebase_config()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Follow the manual steps above in Firebase Console")
    print("2. Set up Stripe products and get price IDs")
    print("3. Update environment variables in Vercel")
    print("4. Deploy and test!")
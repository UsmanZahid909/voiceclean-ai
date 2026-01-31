#!/usr/bin/env python3
"""
Firebase Setup Script for VoiceClean AI
Run this script to set up Firebase project and get configuration
"""

import os
import json

def setup_firebase():
    print("🔥 Firebase Setup for VoiceClean AI")
    print("=" * 50)
    
    print("\n📋 Follow these steps to set up Firebase:")
    print("1. Go to https://console.firebase.google.com/")
    print("2. Click 'Create a project' or 'Add project'")
    print("3. Enter project name: 'voiceclean-ai'")
    print("4. Enable Google Analytics (optional)")
    print("5. Create project")
    
    print("\n🔧 Enable Authentication:")
    print("1. Go to Authentication > Sign-in method")
    print("2. Enable 'Email/Password'")
    print("3. Enable 'Google' sign-in")
    print("4. Add your domain to authorized domains")
    
    print("\n🗄️ Enable Firestore:")
    print("1. Go to Firestore Database")
    print("2. Click 'Create database'")
    print("3. Choose 'Start in test mode'")
    print("4. Select location (us-central1 recommended)")
    
    print("\n🔑 Get Service Account Key:")
    print("1. Go to Project Settings > Service accounts")
    print("2. Click 'Generate new private key'")
    print("3. Download the JSON file")
    print("4. Save it as 'firebase-service-account.json'")
    
    print("\n⚙️ Get Web App Config:")
    print("1. Go to Project Settings > General")
    print("2. Scroll to 'Your apps'")
    print("3. Click 'Web app' icon")
    print("4. Register app with name 'VoiceClean AI'")
    print("5. Copy the config object")
    
    print("\n🌐 Environment Variables to Set:")
    print("FIREBASE_API_KEY=your_api_key")
    print("FIREBASE_AUTH_DOMAIN=voiceclean-ai.firebaseapp.com")
    print("FIREBASE_PROJECT_ID=voiceclean-ai")
    print("FIREBASE_STORAGE_BUCKET=voiceclean-ai.appspot.com")
    print("FIREBASE_MESSAGING_SENDER_ID=your_sender_id")
    print("FIREBASE_APP_ID=your_app_id")
    print("FIREBASE_DATABASE_URL=https://voiceclean-ai-default-rtdb.firebaseio.com/")
    print("FIREBASE_PRIVATE_KEY_ID=your_private_key_id")
    print("FIREBASE_PRIVATE_KEY=your_private_key")
    print("FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@voiceclean-ai.iam.gserviceaccount.com")
    print("FIREBASE_CLIENT_ID=your_client_id")
    
    print("\n💳 Stripe Setup:")
    print("1. Go to https://dashboard.stripe.com/")
    print("2. Create account or sign in")
    print("3. Go to Developers > API keys")
    print("4. Copy Publishable key and Secret key")
    print("5. Create products for Basic ($1/month) and Unlimited ($2/month)")
    print("6. Get price IDs for each product")
    
    print("\n🌐 Environment Variables for Stripe:")
    print("STRIPE_PUBLISHABLE_KEY=pk_test_...")
    print("STRIPE_SECRET_KEY=sk_test_...")
    print("STRIPE_BASIC_PRICE_ID=price_...")
    print("STRIPE_UNLIMITED_PRICE_ID=price_...")
    print("STRIPE_WEBHOOK_SECRET=whsec_...")
    
    print("\n✅ After setup, update these files:")
    print("- Update firebase-config.json with your service account")
    print("- Set environment variables in Vercel dashboard")
    print("- Test authentication and database connection")
    
    print("\n🚀 Ready to deploy with Firebase + Stripe integration!")

if __name__ == "__main__":
    setup_firebase()
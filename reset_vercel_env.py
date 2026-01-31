#!/usr/bin/env python3
"""
Script to reset Vercel environment variables and redeploy
"""

import subprocess
import sys
import json
import os

def run_command(command, description):
    """Run a command and return the result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return result.stdout.strip()
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - Timeout")
        return None
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return None

def main():
    print("🚀 Resetting Vercel Environment Variables")
    print("=" * 50)
    
    # Check if Vercel CLI is installed
    vercel_check = run_command("vercel --version", "Checking Vercel CLI")
    if not vercel_check:
        print("❌ Vercel CLI not found. Installing...")
        install_result = run_command("npm install -g vercel", "Installing Vercel CLI")
        if not install_result:
            print("❌ Failed to install Vercel CLI. Please install manually: npm install -g vercel")
            return
    
    # Login to Vercel (if not already logged in)
    print("\n🔐 Vercel Authentication")
    login_result = run_command("vercel whoami", "Checking Vercel login status")
    if not login_result:
        print("🔑 Please login to Vercel...")
        login_cmd = run_command("vercel login", "Logging into Vercel")
        if not login_cmd:
            print("❌ Failed to login to Vercel")
            return
    
    # Link to project
    print("\n🔗 Linking to Vercel project")
    link_result = run_command("vercel link --yes", "Linking to Vercel project")
    
    # Get current environment variables
    print("\n📋 Getting current environment variables")
    env_list = run_command("vercel env ls", "Listing environment variables")
    
    # Remove all environment variables
    print("\n🗑️ Removing all environment variables")
    
    # Common environment variable names to remove
    env_vars_to_remove = [
        "SECRET_KEY",
        "FIREBASE_API_KEY", 
        "FIREBASE_AUTH_DOMAIN",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_STORAGE_BUCKET",
        "FIREBASE_MESSAGING_SENDER_ID",
        "FIREBASE_APP_ID",
        "FIREBASE_MEASUREMENT_ID",
        "STRIPE_PUBLISHABLE_KEY",
        "STRIPE_SECRET_KEY",
        "ELEVENLABS_API_KEY"
    ]
    
    for var_name in env_vars_to_remove:
        remove_cmd = f"vercel env rm {var_name} production --yes"
        run_command(remove_cmd, f"Removing {var_name}")
        
        remove_cmd_preview = f"vercel env rm {var_name} preview --yes"
        run_command(remove_cmd_preview, f"Removing {var_name} from preview")
        
        remove_cmd_dev = f"vercel env rm {var_name} development --yes"
        run_command(remove_cmd_dev, f"Removing {var_name} from development")
    
    # Add environment variables back
    print("\n➕ Adding environment variables back")
    
    # Firebase Configuration
    firebase_vars = {
        "SECRET_KEY": "voiceclean-ai-secret-key-2024-firebase-complete",
        "FIREBASE_API_KEY": "AIzaSyF29QM3C0pri4z5say9nu4a",
        "FIREBASE_AUTH_DOMAIN": "voiceclean-ai-say9nu4a.firebaseapp.com",
        "FIREBASE_PROJECT_ID": "voiceclean-ai-say9nu4a",
        "FIREBASE_STORAGE_BUCKET": "voiceclean-ai-say9nu4a.appspot.com",
        "FIREBASE_MESSAGING_SENDER_ID": "454829723768",
        "FIREBASE_APP_ID": "1:454829723768:web:ec36f24d8df4f882499d8d",
        "FIREBASE_MEASUREMENT_ID": "G-G35LS3E4P7"
    }
    
    for var_name, var_value in firebase_vars.items():
        add_cmd = f'vercel env add {var_name} production'
        print(f"🔧 Adding {var_name} to production...")
        
        # Use echo to pipe the value to vercel env add
        full_cmd = f'echo "{var_value}" | vercel env add {var_name} production'
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Added {var_name} to production")
        else:
            print(f"❌ Failed to add {var_name}: {result.stderr}")
    
    # Trigger redeployment
    print("\n🚀 Triggering redeployment")
    deploy_result = run_command("vercel --prod", "Deploying to production")
    
    if deploy_result:
        print("\n🎉 Environment variables reset and redeployment complete!")
        print("🔗 Your app should be updated with the new environment variables")
        print("⏰ Wait 2-3 minutes for the deployment to complete")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")

if __name__ == "__main__":
    main()
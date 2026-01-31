#!/usr/bin/env python3
"""
Automatically set up Vercel environment variables
"""

import subprocess
import os
import time

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not installed")
        return False

def install_vercel_cli():
    """Install Vercel CLI"""
    print("📦 Installing Vercel CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
        print("✅ Vercel CLI installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install Vercel CLI: {e}")
        return False

def setup_vercel_env():
    """Set up Vercel environment variables"""
    print("🔧 Setting up Vercel environment variables...")
    
    env_vars = {
        "FIREBASE_API_KEY": "AIzaSyAB3EfEbhUDMB4ZYk6pFTQ6Vl6EC1Sa2fI",
        "FIREBASE_AUTH_DOMAIN": "avian-mystery-433509-u5.firebaseapp.com",
        "FIREBASE_PROJECT_ID": "avian-mystery-433509-u5",
        "FIREBASE_STORAGE_BUCKET": "avian-mystery-433509-u5.firebasestorage.app",
        "FIREBASE_MESSAGING_SENDER_ID": "454829723768",
        "FIREBASE_APP_ID": "1:454829723768:web:ec36f24d8df4f882499d8d",
        "FIREBASE_MEASUREMENT_ID": "G-G35LS3E4P7",
        "SECRET_KEY": "voiceclean-ai-secret-key-2024-firebase"
    }
    
    print("📋 Setting environment variables in Vercel...")
    
    for key, value in env_vars.items():
        try:
            # Use vercel env add command
            process = subprocess.Popen(
                ['vercel', 'env', 'add', key],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send the value and environment selection
            stdout, stderr = process.communicate(input=f"{value}\ny\ny\ny\n")
            
            if process.returncode == 0:
                print(f"✅ Set {key}")
            else:
                print(f"⚠️  {key} - {stderr.strip()}")
                
        except Exception as e:
            print(f"❌ Failed to set {key}: {e}")
    
    print("\n🚀 Triggering redeploy...")
    try:
        subprocess.run(['vercel', '--prod'], check=True)
        print("✅ Redeploy triggered")
    except Exception as e:
        print(f"⚠️  Manual redeploy needed: {e}")

def manual_setup_instructions():
    """Provide manual setup instructions"""
    print("\n📋 MANUAL SETUP INSTRUCTIONS")
    print("=" * 50)
    print("If automatic setup failed, follow these steps:")
    print("\n1. Install Vercel CLI:")
    print("   npm install -g vercel")
    print("\n2. Login to Vercel:")
    print("   vercel login")
    print("\n3. Navigate to your project and link it:")
    print("   vercel link")
    print("\n4. Set environment variables:")
    
    env_vars = {
        "FIREBASE_API_KEY": "AIzaSyAB3EfEbhUDMB4ZYk6pFTQ6Vl6EC1Sa2fI",
        "FIREBASE_AUTH_DOMAIN": "avian-mystery-433509-u5.firebaseapp.com",
        "FIREBASE_PROJECT_ID": "avian-mystery-433509-u5",
        "FIREBASE_STORAGE_BUCKET": "avian-mystery-433509-u5.firebasestorage.app",
        "FIREBASE_MESSAGING_SENDER_ID": "454829723768",
        "FIREBASE_APP_ID": "1:454829723768:web:ec36f24d8df4f882499d8d",
        "FIREBASE_MEASUREMENT_ID": "G-G35LS3E4P7",
        "SECRET_KEY": "voiceclean-ai-secret-key-2024-firebase"
    }
    
    for key, value in env_vars.items():
        print(f"   vercel env add {key}")
        print(f"   # Enter: {value}")
        print(f"   # Select: Production, Preview, Development (y/y/y)")
    
    print("\n5. Redeploy:")
    print("   vercel --prod")
    
    print("\n🌐 Or use Vercel Dashboard:")
    print("1. Go to: https://vercel.com/dashboard")
    print("2. Select 'voiceclean-ai' project")
    print("3. Go to Settings > Environment Variables")
    print("4. Add each variable above")
    print("5. Redeploy from Deployments tab")

def test_deployment():
    """Test deployment after setup"""
    print("\n📋 Testing deployment...")
    time.sleep(30)  # Wait for deployment
    
    import requests
    
    try:
        pages = ['/', '/login', '/signup', '/pricing', '/dashboard']
        working = 0
        
        for page in pages:
            response = requests.get(f"https://voiceclean-ai.vercel.app{page}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {page} - Working")
                working += 1
            else:
                print(f"❌ {page} - Status: {response.status_code}")
        
        if working == len(pages):
            print(f"\n🎉 ALL PAGES WORKING!")
            print(f"🔗 Your app: https://voiceclean-ai.vercel.app")
        else:
            print(f"\n⚠️  {working}/{len(pages)} pages working")
            print(f"🔧 May need additional time for deployment")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    print("🚀 VERCEL ENVIRONMENT SETUP")
    print("=" * 40)
    
    # Check if Vercel CLI is available
    if not check_vercel_cli():
        if not install_vercel_cli():
            manual_setup_instructions()
            return
    
    # Try to set up environment variables
    try:
        setup_vercel_env()
        test_deployment()
    except Exception as e:
        print(f"❌ Automatic setup failed: {e}")
        manual_setup_instructions()

if __name__ == "__main__":
    main()
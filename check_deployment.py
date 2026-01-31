#!/usr/bin/env python3
"""
Check deployment status and redeploy if needed
"""

import subprocess
import time
import requests

def check_deployment():
    print("🚀 Checking VoiceClean AI Deployment Status")
    print("=" * 50)
    
    # Check current deployment
    print("\n📋 Testing current deployment...")
    
    try:
        response = requests.get("https://voiceclean-ai.vercel.app", timeout=10)
        content = response.text
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(content)} bytes")
        
        # Check if it's the full page
        if len(content) < 5000:  # Full page should be much larger
            print("⚠️  Page content seems truncated or incomplete")
            print("🔄 Triggering redeployment...")
            
            # Force redeploy by making a small change and pushing
            redeploy()
        else:
            print("✅ Deployment appears to be working correctly")
            
    except Exception as e:
        print(f"❌ Deployment check failed: {e}")
        print("🔄 Triggering redeployment...")
        redeploy()

def redeploy():
    """Force redeploy by making a small change"""
    try:
        # Update a timestamp in the health endpoint
        print("\n🔄 Forcing redeployment...")
        
        # Make a small change to trigger redeploy
        with open('api/index.py', 'r') as f:
            content = f.read()
        
        # Update version number if it exists
        if 'version' in content:
            import re
            import time
            timestamp = str(int(time.time()))
            content = re.sub(r"'version': '[^']*'", f"'version': 'Firebase-Auth-{timestamp}'", content)
            
            with open('api/index.py', 'w') as f:
                f.write(content)
            
            print("✅ Updated version timestamp")
        
        # Commit and push
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'fix: Force redeploy to fix routing issues'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("✅ Redeployment triggered successfully")
        print("⏳ Waiting for deployment to complete...")
        
        # Wait for deployment
        time.sleep(30)
        
        # Test again
        print("\n📋 Testing after redeployment...")
        response = requests.get("https://voiceclean-ai.vercel.app", timeout=10)
        
        if response.status_code == 200 and len(response.text) > 5000:
            print("✅ Redeployment successful!")
            test_authentication_pages()
        else:
            print("⚠️  Redeployment may still be processing...")
            
    except Exception as e:
        print(f"❌ Redeployment failed: {e}")

def test_authentication_pages():
    """Test authentication pages after deployment"""
    print("\n📋 Testing authentication pages...")
    
    pages = [
        ("/login", "Sign In"),
        ("/signup", "Sign Up"),
        ("/pricing", "Pricing"),
        ("/dashboard", "Dashboard")
    ]
    
    for path, expected in pages:
        try:
            response = requests.get(f"https://voiceclean-ai.vercel.app{path}", timeout=10)
            if response.status_code == 200 and expected.lower() in response.text.lower():
                print(f"✅ {path} - Working correctly")
            else:
                print(f"❌ {path} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {path} - Error: {e}")

if __name__ == "__main__":
    check_deployment()
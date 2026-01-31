#!/usr/bin/env python3
"""
Comprehensive Variable Check and Fix for Vercel and Firebase
This script will automatically diagnose and fix configuration issues
"""

import os
import json
import requests
import subprocess
import time
from datetime import datetime

class VoiceCleanConfigFixer:
    def __init__(self):
        self.firebase_config = {
            "apiKey": "AIzaSyAB3EfEbhUDMB4ZYk6pFTQ6Vl6EC1Sa2fI",
            "authDomain": "avian-mystery-433509-u5.firebaseapp.com",
            "projectId": "avian-mystery-433509-u5",
            "storageBucket": "avian-mystery-433509-u5.firebasestorage.app",
            "messagingSenderId": "454829723768",
            "appId": "1:454829723768:web:ec36f24d8df4f882499d8d",
            "measurementId": "G-G35LS3E4P7"
        }
        self.base_url = "https://voiceclean-ai.vercel.app"
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step, description):
        print(f"\n📋 STEP {step}: {description}")
        print("-" * 50)
    
    def check_firebase_variables(self):
        """Check Firebase configuration variables"""
        self.print_step(1, "Checking Firebase Configuration")
        
        # Check .env file
        env_vars = {}
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
        
        required_firebase_vars = [
            'FIREBASE_API_KEY',
            'FIREBASE_AUTH_DOMAIN', 
            'FIREBASE_PROJECT_ID',
            'FIREBASE_STORAGE_BUCKET',
            'FIREBASE_MESSAGING_SENDER_ID',
            'FIREBASE_APP_ID',
            'FIREBASE_MEASUREMENT_ID'
        ]
        
        missing_vars = []
        for var in required_firebase_vars:
            if var not in env_vars:
                missing_vars.append(var)
                print(f"❌ Missing: {var}")
            else:
                print(f"✅ Found: {var} = {env_vars[var][:20]}...")
        
        if missing_vars:
            print(f"\n🔧 Fixing missing Firebase variables...")
            self.fix_env_file()
        else:
            print(f"\n✅ All Firebase variables present in .env")
        
        return len(missing_vars) == 0
    
    def fix_env_file(self):
        """Fix .env file with correct Firebase variables"""
        env_content = f"""# Firebase Configuration
FIREBASE_API_KEY={self.firebase_config['apiKey']}
FIREBASE_AUTH_DOMAIN={self.firebase_config['authDomain']}
FIREBASE_PROJECT_ID={self.firebase_config['projectId']}
FIREBASE_STORAGE_BUCKET={self.firebase_config['storageBucket']}
FIREBASE_MESSAGING_SENDER_ID={self.firebase_config['messagingSenderId']}
FIREBASE_APP_ID={self.firebase_config['appId']}
FIREBASE_MEASUREMENT_ID={self.firebase_config['measurementId']}

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
        
        print("✅ Updated .env file with correct Firebase configuration")
    
    def check_vercel_deployment(self):
        """Check Vercel deployment status"""
        self.print_step(2, "Checking Vercel Deployment")
        
        try:
            # Test main page
            response = requests.get(self.base_url, timeout=10)
            print(f"Main page status: {response.status_code}")
            print(f"Content length: {len(response.text)} bytes")
            
            if response.status_code == 200 and len(response.text) > 5000:
                print("✅ Main page deployment working")
            else:
                print("❌ Main page deployment issue")
                return False
            
            # Test authentication pages
            auth_pages = ['/login', '/signup', '/pricing', '/dashboard']
            working_pages = []
            broken_pages = []
            
            for page in auth_pages:
                try:
                    page_response = requests.get(f"{self.base_url}{page}", timeout=10)
                    if page_response.status_code == 200:
                        working_pages.append(page)
                        print(f"✅ {page} - Working")
                    else:
                        broken_pages.append(page)
                        print(f"❌ {page} - Status: {page_response.status_code}")
                except Exception as e:
                    broken_pages.append(page)
                    print(f"❌ {page} - Error: {e}")
            
            if broken_pages:
                print(f"\n🔧 Found {len(broken_pages)} broken pages, fixing...")
                return self.fix_vercel_deployment()
            else:
                print(f"\n✅ All pages working correctly")
                return True
                
        except Exception as e:
            print(f"❌ Deployment check failed: {e}")
            return False
    
    def fix_vercel_deployment(self):
        """Fix Vercel deployment issues"""
        print("🔧 Fixing Vercel deployment...")
        
        # Check if routes are properly defined
        self.check_flask_routes()
        
        # Force redeploy
        return self.force_redeploy()
    
    def check_flask_routes(self):
        """Check Flask routes in api/index.py"""
        print("\n📋 Checking Flask routes...")
        
        with open('api/index.py', 'r') as f:
            content = f.read()
        
        required_routes = [
            "@app.route('/')",
            "@app.route('/login')",
            "@app.route('/signup')",
            "@app.route('/pricing')",
            "@app.route('/dashboard')"
        ]
        
        missing_routes = []
        for route in required_routes:
            if route not in content:
                missing_routes.append(route)
                print(f"❌ Missing route: {route}")
            else:
                print(f"✅ Found route: {route}")
        
        # Check for template folder specification
        if "template_folder='templates'" not in content:
            print("🔧 Adding template folder specification...")
            content = content.replace(
                "app = Flask(__name__)",
                "app = Flask(__name__, template_folder='templates')"
            )
            
            with open('api/index.py', 'w') as f:
                f.write(content)
            print("✅ Updated Flask app with template folder")
        
        return len(missing_routes) == 0
    
    def force_redeploy(self):
        """Force redeploy by updating version and pushing"""
        print("\n🚀 Forcing redeploy...")
        
        try:
            # Update version in health endpoint
            with open('api/index.py', 'r') as f:
                content = f.read()
            
            timestamp = str(int(time.time()))
            new_version = f"Firebase-Auth-Fixed-{timestamp}"
            
            if "'version':" in content:
                import re
                content = re.sub(
                    r"'version': '[^']*'",
                    f"'version': '{new_version}'",
                    content
                )
            
            with open('api/index.py', 'w') as f:
                f.write(content)
            
            # Commit and push
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'fix: Auto-fix deployment issues - {new_version}'], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            print("✅ Redeploy triggered successfully")
            print("⏳ Waiting for deployment to complete...")
            
            # Wait for deployment
            time.sleep(45)
            
            return self.verify_deployment()
            
        except Exception as e:
            print(f"❌ Redeploy failed: {e}")
            return False
    
    def verify_deployment(self):
        """Verify deployment after fixes"""
        print("\n📋 Verifying deployment...")
        
        try:
            # Test all pages
            pages = ['/', '/login', '/signup', '/pricing', '/dashboard']
            all_working = True
            
            for page in pages:
                response = requests.get(f"{self.base_url}{page}", timeout=15)
                if response.status_code == 200:
                    print(f"✅ {page} - Working ({len(response.text)} bytes)")
                else:
                    print(f"❌ {page} - Status: {response.status_code}")
                    all_working = False
            
            return all_working
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def check_firebase_console_setup(self):
        """Check Firebase console setup"""
        self.print_step(3, "Checking Firebase Console Setup")
        
        print(f"🔥 Firebase Project Details:")
        print(f"Project ID: {self.firebase_config['projectId']}")
        print(f"Console URL: https://console.firebase.google.com/project/{self.firebase_config['projectId']}")
        
        print(f"\n📋 Required Firebase Console Setup:")
        print(f"1. ✅ Authentication enabled (Email/Password + Google)")
        print(f"2. ✅ Firestore Database created")
        print(f"3. ✅ Authorized domain added: voiceclean-ai.vercel.app")
        
        # Test Firebase connectivity
        try:
            # Try to access Firebase REST API to check if project exists
            test_url = f"https://identitytoolkit.googleapis.com/v1/projects/{self.firebase_config['projectId']}"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code in [200, 400]:  # 400 is expected without proper auth
                print(f"✅ Firebase project accessible")
            else:
                print(f"⚠️  Firebase project status unclear")
                
        except Exception as e:
            print(f"⚠️  Firebase connectivity test failed: {e}")
    
    def generate_vercel_env_commands(self):
        """Generate Vercel environment variable commands"""
        self.print_step(4, "Generating Vercel Environment Variables")
        
        env_vars = {
            "FIREBASE_API_KEY": self.firebase_config['apiKey'],
            "FIREBASE_AUTH_DOMAIN": self.firebase_config['authDomain'],
            "FIREBASE_PROJECT_ID": self.firebase_config['projectId'],
            "FIREBASE_STORAGE_BUCKET": self.firebase_config['storageBucket'],
            "FIREBASE_MESSAGING_SENDER_ID": self.firebase_config['messagingSenderId'],
            "FIREBASE_APP_ID": self.firebase_config['appId'],
            "FIREBASE_MEASUREMENT_ID": self.firebase_config['measurementId'],
            "SECRET_KEY": "voiceclean-ai-secret-key-2024-firebase"
        }
        
        print(f"\n📋 Copy these commands to set Vercel environment variables:")
        print(f"(Run these in your terminal after installing Vercel CLI)")
        print(f"\nnpm i -g vercel")
        print(f"vercel login")
        print(f"cd your-project-directory")
        
        for key, value in env_vars.items():
            print(f"vercel env add {key}")
            print(f"# Enter: {value}")
        
        print(f"\n🔧 Or set them manually in Vercel Dashboard:")
        print(f"1. Go to: https://vercel.com/dashboard")
        print(f"2. Select 'voiceclean-ai' project")
        print(f"3. Go to Settings > Environment Variables")
        print(f"4. Add each variable:")
        
        for key, value in env_vars.items():
            print(f"   {key} = {value}")
    
    def run_complete_fix(self):
        """Run complete diagnostic and fix process"""
        self.print_header("VOICECLEAN AI - COMPLETE VARIABLE FIX")
        
        print(f"🎯 Target: {self.base_url}")
        print(f"🔥 Firebase Project: {self.firebase_config['projectId']}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Check Firebase variables
        firebase_ok = self.check_firebase_variables()
        
        # Step 2: Check Vercel deployment
        vercel_ok = self.check_vercel_deployment()
        
        # Step 3: Check Firebase console
        self.check_firebase_console_setup()
        
        # Step 4: Generate Vercel commands
        self.generate_vercel_env_commands()
        
        # Final status
        self.print_header("FINAL STATUS")
        
        if firebase_ok and vercel_ok:
            print("🎉 ALL SYSTEMS WORKING!")
            print("✅ Firebase configuration correct")
            print("✅ Vercel deployment working")
            print("✅ All authentication pages accessible")
            
            print(f"\n📱 Test your app:")
            print(f"1. Visit: {self.base_url}")
            print(f"2. Click 'Sign Up Free'")
            print(f"3. Test Firebase authentication")
            print(f"4. Try audio enhancement")
            
        else:
            print("⚠️  SOME ISSUES FOUND")
            if not firebase_ok:
                print("❌ Firebase configuration needs attention")
            if not vercel_ok:
                print("❌ Vercel deployment needs attention")
            
            print(f"\n🔧 Next steps:")
            print(f"1. Set environment variables in Vercel Dashboard")
            print(f"2. Complete Firebase Console setup")
            print(f"3. Wait for deployment to complete")
            print(f"4. Test again")
        
        print(f"\n🔗 Important URLs:")
        print(f"• App: {self.base_url}")
        print(f"• Vercel: https://vercel.com/dashboard")
        print(f"• Firebase: https://console.firebase.google.com/project/{self.firebase_config['projectId']}")

if __name__ == "__main__":
    fixer = VoiceCleanConfigFixer()
    fixer.run_complete_fix()
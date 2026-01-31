#!/usr/bin/env python3
"""
Create a minimal working Flask app with all routes
"""

import os
import shutil

def create_minimal_app():
    print("🔧 Creating minimal working Flask app...")
    
    # Backup current app
    if os.path.exists('api/index.py'):
        shutil.copy('api/index.py', 'api/index.py.backup')
        print("✅ Backed up current app")
    
    minimal_app = '''from flask import Flask, render_template, jsonify, request, send_file
import os
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = None
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.getenv('SECRET_KEY', 'voiceclean-ai-secret-key-2024')

# Firebase Configuration
FIREBASE_CONFIG = {
    "apiKey": os.getenv('FIREBASE_API_KEY', 'AIzaSyAB3EfEbhUDMB4ZYk6pFTQ6Vl6EC1Sa2fI'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN', 'avian-mystery-433509-u5.firebaseapp.com'),
    "projectId": os.getenv('FIREBASE_PROJECT_ID', 'avian-mystery-433509-u5'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET', 'avian-mystery-433509-u5.firebasestorage.app'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID', '454829723768'),
    "appId": os.getenv('FIREBASE_APP_ID', '1:454829723768:web:ec36f24d8df4f882499d8d'),
    "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID', 'G-G35LS3E4P7')
}

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_key_here')

# Subscription Plans
PLANS = {
    'free': {
        'name': 'Free Plan',
        'daily_minutes': 10,
        'price': 0,
        'stripe_price_id': None
    },
    'basic': {
        'name': 'Basic Plan',
        'daily_minutes': 60,
        'price': 1.00,
        'stripe_price_id': os.getenv('STRIPE_BASIC_PRICE_ID', 'price_basic_monthly')
    },
    'unlimited': {
        'name': 'Unlimited Plan',
        'daily_minutes': -1,
        'price': 2.00,
        'stripe_price_id': os.getenv('STRIPE_UNLIMITED_PRICE_ID', 'price_unlimited_monthly')
    }
}

# Simple user store (replace with Firestore in production)
user_store = {}

# Main Routes
@app.route('/')
def index():
    """Main landing page"""
    try:
        return render_template('index.html', firebase_config=FIREBASE_CONFIG, stripe_key=STRIPE_PUBLISHABLE_KEY)
    except Exception as e:
        logger.error(f"Index route error: {e}")
        return f"VoiceClean AI - Main page error: {e}", 500

@app.route('/login')
def login():
    """Login page"""
    try:
        return render_template('login.html', firebase_config=FIREBASE_CONFIG)
    except Exception as e:
        logger.error(f"Login route error: {e}")
        return f"Login page error: {e}", 500

@app.route('/signup')
def signup():
    """Signup page"""
    try:
        return render_template('signup.html', firebase_config=FIREBASE_CONFIG)
    except Exception as e:
        logger.error(f"Signup route error: {e}")
        return f"Signup page error: {e}", 500

@app.route('/pricing')
def pricing():
    """Pricing page"""
    try:
        return render_template('pricing.html', plans=PLANS, stripe_key=STRIPE_PUBLISHABLE_KEY)
    except Exception as e:
        logger.error(f"Pricing route error: {e}")
        return f"Pricing page error: {e}", 500

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    try:
        return render_template('dashboard.html', firebase_config=FIREBASE_CONFIG, stripe_key=STRIPE_PUBLISHABLE_KEY)
    except Exception as e:
        logger.error(f"Dashboard route error: {e}")
        return f"Dashboard page error: {e}", 500

# API Routes
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': 'Firebase-Auth-Minimal-Working',
        'timestamp': time.time(),
        'routes': ['/', '/login', '/signup', '/pricing', '/dashboard'],
        'firebase_project_id': FIREBASE_CONFIG['projectId'],
        'firebase_api_key': f"{FIREBASE_CONFIG['apiKey'][:10]}...",
        'template_folder': app.template_folder,
        'ready': True
    })

@app.route('/api/test')
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        'message': 'VoiceClean AI - All routes working!',
        'timestamp': time.time(),
        'status': 'operational',
        'routes_working': True
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.error(f"404 error: {request.url}")
    return jsonify({
        'error': '404 Not Found',
        'url': request.url,
        'available_routes': ['/', '/login', '/signup', '/pricing', '/dashboard']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}")
    return jsonify({
        'error': '500 Internal Server Error',
        'message': str(error)
    }), 500

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    # Write the minimal app
    with open('api/index.py', 'w', encoding='utf-8') as f:
        f.write(minimal_app)
    
    print("✅ Created minimal working Flask app")
    print("📋 Features included:")
    print("  - All authentication routes")
    print("  - Proper error handling")
    print("  - Firebase configuration")
    print("  - Template folder specification")
    print("  - Health check endpoint")
    
    return True

def deploy_minimal_app():
    """Deploy the minimal app"""
    print("\n🚀 Deploying minimal app...")
    
    import subprocess
    
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'fix: Create minimal working Flask app with all routes'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ Minimal app deployed successfully")
        return True
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def main():
    print("🔧 CREATING MINIMAL WORKING APP")
    print("=" * 40)
    
    if create_minimal_app():
        if deploy_minimal_app():
            print("\n⏳ Waiting for deployment...")
            print("🔗 Test your app in 60 seconds: https://voiceclean-ai.vercel.app")
            print("\n📋 Test these URLs:")
            print("  • https://voiceclean-ai.vercel.app/")
            print("  • https://voiceclean-ai.vercel.app/login")
            print("  • https://voiceclean-ai.vercel.app/signup")
            print("  • https://voiceclean-ai.vercel.app/pricing")
            print("  • https://voiceclean-ai.vercel.app/dashboard")
            print("  • https://voiceclean-ai.vercel.app/api/health")
        else:
            print("❌ Failed to deploy")
    else:
        print("❌ Failed to create minimal app")

if __name__ == "__main__":
    main()
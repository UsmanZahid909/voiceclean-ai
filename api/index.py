from flask import Flask, render_template, jsonify
import os
import time

app = Flask(__name__, template_folder='templates')
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
    'free': {'name': 'Free Plan', 'daily_minutes': 10, 'price': 0},
    'basic': {'name': 'Basic Plan', 'daily_minutes': 60, 'price': 1.00},
    'unlimited': {'name': 'Unlimited Plan', 'daily_minutes': -1, 'price': 2.00}
}

@app.route('/')
def index():
    return render_template('index.html', firebase_config=FIREBASE_CONFIG, stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/login')
def login():
    return render_template('login.html', firebase_config=FIREBASE_CONFIG)

@app.route('/signup')
def signup():
    return render_template('signup.html', firebase_config=FIREBASE_CONFIG)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', plans=PLANS, stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', firebase_config=FIREBASE_CONFIG, stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': 'Firebase-Auth-Working',
        'timestamp': time.time(),
        'routes': ['/', '/login', '/signup', '/pricing', '/dashboard'],
        'firebase_project_id': FIREBASE_CONFIG['projectId'],
        'ready': True
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '404 Not Found', 'available_routes': ['/', '/login', '/signup', '/pricing', '/dashboard']}), 404

if __name__ == '__main__':
    app.run(debug=True)
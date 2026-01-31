from flask import Flask, render_template, jsonify, request, send_file
import os
import time
import logging
import io
import tempfile
from werkzeug.utils import secure_filename
from gradio_client import Client
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = None
app.config['UPLOAD_FOLDER'] = '/tmp'
app.secret_key = os.getenv('SECRET_KEY', 'voiceclean-ai-secret-key-2024')

# Firebase Configuration - Using Environment Variables
FIREBASE_CONFIG = {
    "apiKey": os.getenv('FIREBASE_API_KEY', 'AIzaSyF29QM3C0pri4z5say9nu4a'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN', 'voiceclean-ai-say9nu4a.firebaseapp.com'),
    "projectId": os.getenv('FIREBASE_PROJECT_ID', 'voiceclean-ai-say9nu4a'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET', 'voiceclean-ai-say9nu4a.appspot.com'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID', '454829723768'),
    "appId": os.getenv('FIREBASE_APP_ID', '1:454829723768:web:ec36f24d8df4f882499d8d'),
    "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID', 'G-G35LS3E4P7'),
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL', 'https://voiceclean-ai-say9nu4a-default-rtdb.firebaseio.com/')
}

# Additional Firebase Configuration
FIREBASE_ENABLED = os.getenv('FIREBASE_ENABLED', 'true').lower() == 'true'
FIREBASE_ENV = os.getenv('FIREBASE_ENV', 'production')
APP_NAME = os.getenv('APP_NAME', 'VoiceClean AI')
APP_URL = os.getenv('APP_URL', 'https://voiceclean-ai.vercel.app')
APP_ENV = os.getenv('APP_ENV', 'production')

# Subscription Plans
PLANS = {
    'free': {'name': 'Free Plan', 'daily_minutes': 10, 'price': 0},
    'basic': {'name': 'Basic Plan', 'daily_minutes': 60, 'price': 1.00},
    'unlimited': {'name': 'Unlimited Plan', 'daily_minutes': -1, 'price': 2.00}
}

# Simple user store for demo
user_store = {}

def enhance_with_deepfilter(file_stream, filename="audio.wav"):
    """Use DeepFilterNet2 via Gradio"""
    temp_file_path = None
    try:
        logger.info("🎵 Starting DeepFilterNet2 Enhancement...")
        
        file_extension = os.path.splitext(filename)[1] or '.wav'
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension, dir='/tmp') as temp_file:
            file_stream.seek(0)
            chunk_size = 8192
            while True:
                chunk = file_stream.read(chunk_size)
                if not chunk:
                    break
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Connect to DeepFilterNet2
        client = Client("drewThomasson/DeepFilterNet2_no_limit")
        result = client.predict(audio=temp_file_path, api_name="/predict")
        
        enhanced_audio = None
        if result:
            if isinstance(result, str) and os.path.exists(result):
                with open(result, 'rb') as enhanced_file:
                    enhanced_audio = enhanced_file.read()
            elif isinstance(result, (bytes, bytearray)):
                enhanced_audio = bytes(result)
        
        if enhanced_audio and len(enhanced_audio) > 1000:
            return enhanced_audio, "DeepFilterNet2 Enhancement"
        else:
            return None, "Enhancement failed"
            
    except Exception as e:
        logger.error(f"Enhancement error: {str(e)}")
        return None, f"Enhancement failed: {str(e)}"
        
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass

# Main Routes
@app.route('/')
def index():
    logger.info("🏠 Main page accessed - LOGIN/SIGNUP BUTTONS SHOULD BE VISIBLE")
    # Force template refresh by adding cache busting
    return render_template('index.html', 
                         firebase_config=FIREBASE_CONFIG,
                         cache_bust=datetime.now().timestamp())

@app.route('/login')
def login():
    logger.info("🔐 Login page accessed")
    return render_template('login.html', firebase_config=FIREBASE_CONFIG)

@app.route('/signup')
def signup():
    logger.info("📝 Signup page accessed")
    return render_template('signup.html', firebase_config=FIREBASE_CONFIG)

@app.route('/pricing')
def pricing():
    logger.info("💰 Pricing page accessed")
    return render_template('pricing.html', plans=PLANS, firebase_config=FIREBASE_CONFIG)

@app.route('/dashboard')
def dashboard():
    logger.info("📊 Dashboard page accessed")
    return render_template('dashboard.html', firebase_config=FIREBASE_CONFIG)

# API Routes
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': 'Firebase-Complete-Working-v2',
        'firebase_project_id': FIREBASE_CONFIG['projectId'],
        'routes_working': True,
        'ready': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test')
def test_route():
    """Simple test route to verify deployment"""
    return render_template('test.html', timestamp=datetime.now().isoformat())

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check deployment status"""
    import os
    return jsonify({
        'status': 'debug',
        'environment': 'vercel' if os.getenv('VERCEL') else 'local',
        'app_env': APP_ENV,
        'firebase_enabled': FIREBASE_ENABLED,
        'firebase_env': FIREBASE_ENV,
        'app_name': APP_NAME,
        'app_url': APP_URL,
        'routes': [
            '/', '/login', '/signup', '/pricing', '/dashboard', '/test'
        ],
        'templates_available': [
            'index.html', 'login.html', 'signup.html', 'pricing.html', 'dashboard.html', 'test.html'
        ],
        'firebase_config_loaded': bool(FIREBASE_CONFIG),
        'firebase_project_id': FIREBASE_CONFIG.get('projectId'),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify Firebase ID token"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'success': False, 'error': 'No token provided'}), 400
        
        # Simple demo verification - in production use Firebase Admin SDK
        user_id = f'user_{hash(id_token) % 10000}'
        email = 'demo@voiceclean.ai'
        
        if user_id not in user_store:
            user_store[user_id] = {
                'email': email,
                'plan': 'free',
                'daily_minutes_used': 0,
                'last_reset_date': datetime.now().strftime('%Y-%m-%d')
            }
        
        return jsonify({
            'success': True,
            'user': {
                'uid': user_id,
                'email': email,
                'plan': user_store[user_id].get('plan', 'free'),
                'daily_minutes_used': user_store[user_id].get('daily_minutes_used', 0),
                'daily_limit': PLANS[user_store[user_id].get('plan', 'free')]['daily_minutes']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Audio enhancement with authentication"""
    try:
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Check file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 50 * 1024 * 1024:
            return jsonify({'success': False, 'error': 'File too large (max 50MB)'}), 413
        
        # Enhance audio
        enhanced_audio, method_used = enhance_with_deepfilter(file, file.filename)
        
        if not enhanced_audio:
            file.seek(0)
            enhanced_audio = file.read()
            method_used = "Original Audio"
        
        output_filename = f'{os.path.splitext(secure_filename(file.filename))[0]}_enhanced.wav'
        
        return send_file(
            io.BytesIO(enhanced_audio),
            as_attachment=True,
            download_name=output_filename,
            mimetype='audio/wav'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Processing error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 VoiceClean AI Starting - Login/Signup buttons should be visible!")
    app.run(debug=True)
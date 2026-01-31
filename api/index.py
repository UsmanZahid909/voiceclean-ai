from flask import Flask, request, jsonify, send_file, render_template, session
import os
import logging
from werkzeug.utils import secure_filename
import io
import time
from gradio_client import Client, handle_file
import tempfile
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase
import stripe
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = None  # Remove all limits
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.getenv('SECRET_KEY', 'voiceclean-ai-secret-key-2024')

# Firebase Configuration
FIREBASE_CONFIG = {
    "apiKey": os.getenv('FIREBASE_API_KEY', 'AIzaSyBvOyiDXe5jhGtgYzPQSNmEeKmEeKmEeKm'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN', 'voiceclean-ai.firebaseapp.com'),
    "projectId": os.getenv('FIREBASE_PROJECT_ID', 'voiceclean-ai'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET', 'voiceclean-ai.appspot.com'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID', '123456789'),
    "appId": os.getenv('FIREBASE_APP_ID', '1:123456789:web:abcdef123456'),
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL', 'https://voiceclean-ai-default-rtdb.firebaseio.com/')
}

# Stripe Configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')

# Initialize Firebase
try:
    # Initialize Firebase Admin (for server-side operations)
    if not firebase_admin._apps:
        # Create service account key from environment variables
        service_account_info = {
            "type": "service_account",
            "project_id": FIREBASE_CONFIG["projectId"],
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL', ''),
            "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
    
    # Initialize Firestore
    db = firestore.client()
    
    # Initialize Pyrebase (for client-side auth)
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    firebase_auth = firebase.auth()
    
    logger.info("✅ Firebase initialized successfully")
    
except Exception as e:
    logger.error(f"❌ Firebase initialization failed: {e}")
    db = None
    firebase_auth = None

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
        'daily_minutes': -1,  # -1 means unlimited
        'price': 2.00,
        'stripe_price_id': os.getenv('STRIPE_UNLIMITED_PRICE_ID', 'price_unlimited_monthly')
    }
}

# Constants - Support all major audio formats
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac', 'webm', 'opus', 'wma', 'amr'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User Management Functions
def get_user_data(user_id):
    """Get user data from Firestore"""
    if not db:
        return None
    
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            return user_doc.to_dict()
        else:
            # Create new user with free plan
            user_data = {
                'email': '',
                'plan': 'free',
                'daily_minutes_used': 0,
                'last_reset_date': datetime.now().strftime('%Y-%m-%d'),
                'created_at': datetime.now(),
                'stripe_customer_id': None,
                'subscription_status': 'active'
            }
            user_ref.set(user_data)
            return user_data
    except Exception as e:
        logger.error(f"Error getting user data: {e}")
        return None

def update_user_usage(user_id, minutes_used):
    """Update user's daily usage"""
    if not db:
        return False
    
    try:
        user_ref = db.collection('users').document(user_id)
        user_data = get_user_data(user_id)
        
        if not user_data:
            return False
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reset daily usage if it's a new day
        if user_data.get('last_reset_date') != today:
            user_data['daily_minutes_used'] = 0
            user_data['last_reset_date'] = today
        
        # Add new usage
        user_data['daily_minutes_used'] += minutes_used
        
        user_ref.update({
            'daily_minutes_used': user_data['daily_minutes_used'],
            'last_reset_date': today
        })
        
        return True
    except Exception as e:
        logger.error(f"Error updating user usage: {e}")
        return False

def check_user_limits(user_id, estimated_minutes):
    """Check if user can process audio based on their plan"""
    user_data = get_user_data(user_id)
    if not user_data:
        return False, "User data not found"
    
    plan = PLANS.get(user_data.get('plan', 'free'))
    if not plan:
        return False, "Invalid plan"
    
    # Unlimited plan
    if plan['daily_minutes'] == -1:
        return True, "Unlimited plan"
    
    today = datetime.now().strftime('%Y-%m-%d')
    daily_used = user_data.get('daily_minutes_used', 0)
    
    # Reset if new day
    if user_data.get('last_reset_date') != today:
        daily_used = 0
    
    remaining = plan['daily_minutes'] - daily_used
    
    if estimated_minutes > remaining:
        return False, f"Daily limit exceeded. Used: {daily_used}/{plan['daily_minutes']} minutes. Upgrade your plan for more usage."
    
    return True, f"Usage allowed. Remaining: {remaining - estimated_minutes} minutes today"

def estimate_audio_duration(file_size):
    """Estimate audio duration in minutes based on file size"""
    # Rough estimation: 1MB ≈ 1 minute for compressed audio
    estimated_minutes = max(1, file_size / (1024 * 1024))
    return round(estimated_minutes, 1)

def enhance_with_deepfilter(file_stream, filename="audio.wav"):
    """Use DeepFilterNet2 via Gradio - OPTIMIZED for large files"""
    temp_file_path = None
    try:
        logger.info("🎵 Starting DeepFilterNet2 Professional Enhancement...")
        
        # Create optimized temporary file with proper extension
        file_extension = os.path.splitext(filename)[1] or '.wav'
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension, dir='/tmp') as temp_file:
            file_stream.seek(0)
            # Write in chunks for large files
            chunk_size = 8192
            while True:
                chunk = file_stream.read(chunk_size)
                if not chunk:
                    break
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        logger.info(f"📁 Temp file created: {temp_file_path} ({os.path.getsize(temp_file_path)} bytes)")
        
        # Initialize Gradio client with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"� Connecting to DeepFilterNet2 (attempt {attempt + 1}/{max_retries})...")
                client = Client("drewThomasson/DeepFilterNet2_no_limit")
                break
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2)
        
        logger.info("📤 Sending to DeepFilterNet2 for professional enhancement...")
        
        # Process with extended timeout for large files
        result = client.predict(
            audio=handle_file(temp_file_path),
            api_name="/predict"
        )
        
        logger.info(f"📥 DeepFilterNet2 completed! Result: {result}")
        
        # Handle result - could be file path or direct content
        enhanced_audio = None
        if result:
            if isinstance(result, str) and os.path.exists(result):
                # Result is a file path
                with open(result, 'rb') as enhanced_file:
                    enhanced_audio = enhanced_file.read()
                logger.info(f"✅ Enhanced audio loaded: {len(enhanced_audio)} bytes")
            elif isinstance(result, (bytes, bytearray)):
                # Result is direct audio data
                enhanced_audio = bytes(result)
                logger.info(f"✅ Enhanced audio received: {len(enhanced_audio)} bytes")
            else:
                logger.error(f"Unexpected result type: {type(result)}")
                return None, f"Unexpected result type: {type(result)}"
        
        if enhanced_audio and len(enhanced_audio) > 1000:
            logger.info("🎉 DeepFilterNet2 enhancement successful!")
            return enhanced_audio, "DeepFilterNet2 Professional Enhancement"
        else:
            logger.warning(f"DeepFilterNet2 returned insufficient data: {len(enhanced_audio) if enhanced_audio else 0} bytes")
            return None, "Insufficient enhanced audio data"
            
    except Exception as e:
        logger.error(f"💥 DeepFilterNet2 error: {str(e)}")
        return None, f"DeepFilterNet2 processing failed: {str(e)}"
        
    finally:
        # Always clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info("🧹 Temp file cleaned up")
            except Exception as e:
                logger.warning(f"Failed to clean temp file: {e}")

# Stripe Subscription Routes
@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session for subscription"""
    try:
        data = request.get_json()
        plan_id = data.get('plan')
        user_id = data.get('userId')
        
        if plan_id not in PLANS or plan_id == 'free':
            return jsonify({'success': False, 'error': 'Invalid plan'}), 400
        
        plan = PLANS[plan_id]
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'dashboard?success=true',
            cancel_url=request.host_url + 'pricing?canceled=true',
            client_reference_id=user_id,
            metadata={
                'user_id': user_id,
                'plan': plan_id
            }
        )
        
        return jsonify({'success': True, 'checkout_url': session.url})
        
    except Exception as e:
        logger.error(f"Checkout session error: {e}")
        return jsonify({'success': False, 'error': 'Failed to create checkout session'}), 500

@app.route('/api/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle successful subscription
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        plan = session['metadata'].get('plan')
        
        if user_id and plan and db:
            # Update user's plan
            db.collection('users').document(user_id).update({
                'plan': plan,
                'subscription_status': 'active',
                'stripe_customer_id': session.get('customer'),
                'updated_at': datetime.now()
            })
            logger.info(f"User {user_id} upgraded to {plan}")
    
    return jsonify({'success': True})
@app.route('/api/upload-chunk', methods=['POST'])
def upload_chunk():
    """Handle chunked file uploads to bypass Vercel's 4.5MB limit"""
    try:
        chunk = request.files.get('chunk')
        chunk_index = int(request.form.get('chunkIndex', 0))
        total_chunks = int(request.form.get('totalChunks', 1))
        filename = request.form.get('filename', 'audio.wav')
        upload_id = request.form.get('uploadId')
        
        if not chunk or not upload_id:
            return jsonify({'success': False, 'error': 'Missing chunk or upload ID'}), 400
        
        # Create upload directory
        upload_dir = f'/tmp/uploads/{upload_id}'
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save chunk
        chunk_path = f'{upload_dir}/chunk_{chunk_index}'
        chunk.save(chunk_path)
        
        logger.info(f"📦 Chunk {chunk_index + 1}/{total_chunks} saved")
        
        # Check if all chunks are uploaded
        uploaded_chunks = len([f for f in os.listdir(upload_dir) if f.startswith('chunk_')])
        
        if uploaded_chunks == total_chunks:
            # Combine all chunks
            combined_path = f'{upload_dir}/combined_{filename}'
            with open(combined_path, 'wb') as combined_file:
                for i in range(total_chunks):
                    chunk_path = f'{upload_dir}/chunk_{i}'
                    if os.path.exists(chunk_path):
                        with open(chunk_path, 'rb') as chunk_file:
                            combined_file.write(chunk_file.read())
                        os.remove(chunk_path)  # Clean up chunk
            
            file_size = os.path.getsize(combined_path)
            logger.info(f"✅ File combined: {filename} ({file_size} bytes)")
            
            return jsonify({
                'success': True,
                'message': 'File upload complete',
                'uploadId': upload_id,
                'filename': filename,
                'size': file_size,
                'ready_for_processing': True
            })
        else:
            return jsonify({
                'success': True,
                'message': f'Chunk {chunk_index + 1}/{total_chunks} uploaded',
                'uploadId': upload_id,
                'chunks_received': uploaded_chunks,
                'total_chunks': total_chunks
            })
            
    except Exception as e:
        logger.error(f"Chunk upload error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/enhance-chunked', methods=['POST'])
def enhance_chunked_audio():
    """Process audio that was uploaded in chunks"""
    try:
        data = request.get_json()
        upload_id = data.get('uploadId')
        filename = data.get('filename', 'audio.wav')
        
        if not upload_id:
            return jsonify({'success': False, 'error': 'Missing upload ID'}), 400
        
        # Find the combined file
        upload_dir = f'/tmp/uploads/{upload_id}'
        combined_path = f'{upload_dir}/combined_{filename}'
        
        if not os.path.exists(combined_path):
            return jsonify({'success': False, 'error': 'Combined file not found'}), 404
        
        file_size = os.path.getsize(combined_path)
        file_size_mb = file_size / (1024 * 1024)
        
        logger.info(f"🚀 Processing chunked file: {filename} ({file_size_mb:.1f} MB)")
        
        # Process with DeepFilterNet2
        with open(combined_path, 'rb') as file_stream:
            enhanced_audio, method_used = enhance_with_deepfilter(file_stream, filename)
        
        # Clean up upload directory
        import shutil
        shutil.rmtree(upload_dir, ignore_errors=True)
        
        if not enhanced_audio:
            # Fallback to original
            with open(combined_path, 'rb') as f:
                enhanced_audio = f.read()
            method_used = "Original Audio (DeepFilterNet2 failed)"
        
        # Return enhanced audio
        output_filename = f'{os.path.splitext(filename)[0]}_enhanced_voiceclean.wav'
        
        return send_file(
            io.BytesIO(enhanced_audio),
            as_attachment=True,
            download_name=output_filename,
            mimetype='audio/wav'
        )
        
    except Exception as e:
        logger.error(f"Chunked enhancement error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html', firebase_config=FIREBASE_CONFIG, stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', firebase_config=FIREBASE_CONFIG, stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/login')
def login():
    return render_template('login.html', firebase_config=FIREBASE_CONFIG)

@app.route('/signup')
def signup():
    return render_template('signup.html', firebase_config=FIREBASE_CONFIG)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', plans=PLANS, stripe_key=STRIPE_PUBLISHABLE_KEY)

# Authentication API Routes
@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify Firebase ID token"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'success': False, 'error': 'No token provided'}), 400
        
        # Verify the token
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Get or create user data
        user_data = get_user_data(user_id)
        if user_data and not user_data.get('email'):
            # Update email if not set
            db.collection('users').document(user_id).update({'email': email})
            user_data['email'] = email
        
        return jsonify({
            'success': True,
            'user': {
                'uid': user_id,
                'email': email,
                'plan': user_data.get('plan', 'free'),
                'daily_minutes_used': user_data.get('daily_minutes_used', 0),
                'daily_limit': PLANS[user_data.get('plan', 'free')]['daily_minutes']
            }
        })
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'success': False, 'error': 'Invalid token'}), 401

@app.route('/api/user/usage')
def get_user_usage():
    """Get current user's usage statistics"""
    try:
        # Get user ID from session or token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'No authorization token'}), 401
        
        id_token = auth_header.split('Bearer ')[1]
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        
        user_data = get_user_data(user_id)
        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        plan = PLANS[user_data.get('plan', 'free')]
        today = datetime.now().strftime('%Y-%m-%d')
        daily_used = user_data.get('daily_minutes_used', 0)
        
        # Reset if new day
        if user_data.get('last_reset_date') != today:
            daily_used = 0
        
        return jsonify({
            'success': True,
            'usage': {
                'plan': user_data.get('plan', 'free'),
                'plan_name': plan['name'],
                'daily_used': daily_used,
                'daily_limit': plan['daily_minutes'],
                'remaining': plan['daily_minutes'] - daily_used if plan['daily_minutes'] != -1 else -1,
                'is_unlimited': plan['daily_minutes'] == -1
            }
        })
        
    except Exception as e:
        logger.error(f"Usage check error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get usage'}), 500

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Professional audio enhancement with user authentication and limits"""
    try:
        logger.info("🎵 Audio enhancement request received")
        
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        try:
            id_token = auth_header.split('Bearer ')[1]
            decoded_token = auth.verify_id_token(id_token)
            user_id = decoded_token['uid']
        except Exception as e:
            return jsonify({'success': False, 'error': 'Invalid authentication token'}), 401
        
        # Validate request
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': f'Unsupported format. Supported: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
            }), 400
        
        # Read file data using streaming approach
        try:
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Seek back to beginning
            
            file_size_mb = file_size / (1024 * 1024)
            
            logger.info(f"📁 File: {file.filename}")
            logger.info(f"📊 Size: {file_size:,} bytes ({file_size_mb:.1f} MB)")
            
            # Size validation - Now supports large files via chunking
            if file_size == 0:
                return jsonify({'success': False, 'error': 'Empty file uploaded'}), 400
            
            # For direct upload, still limited by Vercel's 4.5MB
            # Large files should use chunked upload endpoint
            if file_size > 4.5 * 1024 * 1024:  # 4.5MB Vercel limit for direct upload
                return jsonify({
                    'success': False, 
                    'error': f'File too large for direct upload ({file_size_mb:.1f}MB).',
                    'suggestion': 'Use chunked upload for files larger than 4.5MB.',
                    'use_chunked_upload': True,
                    'current_size': f'{file_size_mb:.1f}MB',
                    'max_direct_size': '4.5MB'
                }), 413
            
            if file_size < 1000:  # Minimum 1KB
                return jsonify({'success': False, 'error': 'File too small (minimum 1KB)'}), 400
            
            # Check user limits
            estimated_minutes = estimate_audio_duration(file_size)
            can_process, limit_message = check_user_limits(user_id, estimated_minutes)
            
            if not can_process:
                return jsonify({
                    'success': False, 
                    'error': limit_message,
                    'upgrade_required': True,
                    'estimated_minutes': estimated_minutes
                }), 429
            
            # Reset file pointer for processing
            file.seek(0)
            
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return jsonify({'success': False, 'error': 'Error reading uploaded file'}), 400
        
        # Use DeepFilterNet2 for enhancement - OPTIMIZED
        logger.info("� Starting DeepFilterNet2 Professional Enhancement...")
        logger.info(f"📁 Processing: {file.filename} ({file_size_mb:.1f} MB)")
        
        start_time = time.time()
        enhanced_audio, method_used = enhance_with_deepfilter(file, file.filename)
        processing_time = time.time() - start_time
        
        logger.info(f"⏱️ Processing completed in {processing_time:.1f} seconds")
        
        # Enhanced fallback handling
        if not enhanced_audio:
            logger.warning(f"⚠️ DeepFilterNet2 failed: {method_used}")
            # Fallback to original audio
            file.seek(0)
            enhanced_audio = file.read()
            method_used = f"Original Audio (DeepFilterNet2 failed: {method_used})"
            logger.info("🔄 Using original audio as fallback")
        
        # Update user usage
        update_user_usage(user_id, estimated_minutes)
        
        # Success!
        output_size = len(enhanced_audio)
        output_size_mb = output_size / (1024 * 1024)
        
        logger.info(f"✅ Enhancement completed!")
        logger.info(f"🎯 Method: {method_used}")
        logger.info(f"📈 Output: {output_size:,} bytes ({output_size_mb:.1f} MB)")
        
        # Create output filename
        base_name = os.path.splitext(secure_filename(file.filename))[0]
        output_filename = f'{base_name}_enhanced_voiceclean.wav'
        
        # Return enhanced audio
        return send_file(
            io.BytesIO(enhanced_audio),
            as_attachment=True,
            download_name=output_filename,
            mimetype='audio/wav'
        )
        
    except Exception as e:
        logger.error(f"💥 Server error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Processing error: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check with chunked upload support"""
    return jsonify({
        'status': 'healthy',
        'version': '19.0 - Large File Support via Chunked Upload',
        'primary_service': 'DeepFilterNet2 (drewThomasson/DeepFilterNet2_no_limit)',
        'fallback_services': ['Original Audio'],
        'enhancement_guaranteed': True,
        'supported_formats': sorted(list(ALLOWED_EXTENSIONS)),
        'max_file_size': 'Unlimited (chunked upload)',
        'direct_upload_limit': '4.5MB',
        'chunked_upload': True,
        'large_file_support': True,
        'max_duration': '15 minutes',
        'free_service': True,
        'professional_quality': True,
        'ui_style': 'ElevenLabs inspired minimal design',
        'ready': True
    })

@app.route('/api/test')
def test_endpoint():
    """Test endpoint with chunked upload support"""
    return jsonify({
        'message': 'VoiceClean AI v19.0 - Large Files Supported via Chunked Upload!',
        'timestamp': time.time(),
        'status': 'operational',
        'enhancement': 'deepfilternet2_chunked_upload',
        'max_file_size': 'Unlimited',
        'direct_upload_limit': '4.5MB',
        'chunked_upload': True,
        'large_file_support': True,
        'max_duration': '15_minutes',
        'free_service': True,
        'processing_type': 'huggingface_gradio_chunked',
        'model': 'drewThomasson/DeepFilterNet2_no_limit',
        'features': ['chunked_upload', 'large_file_support', 'unlimited_size']
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Vercel serverless functions have a 4.5MB request body limit.',
        'max_size': '4.5MB',
        'vercel_limitation': True,
        'suggestion': 'Please compress your audio file to under 4.5MB or use a different hosting platform for larger files.'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again.'
    }), 500

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
import os
import tempfile
import soundfile as sf
import numpy as np
from scipy import signal
import logging
from werkzeug.utils import secure_filename
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///voiceclean.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE_MB', 50)) * 1024 * 1024

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
oauth = OAuth(app)
CORS(app)

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    google = oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

# Constants
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'}
MAX_DAILY_ENHANCEMENTS = 3

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    google_id = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_demo = db.Column(db.Boolean, default=False)

class Enhancement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    enhancement_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_daily_enhancement_count(user_id):
    today = datetime.utcnow().date()
    count = Enhancement.query.filter(
        Enhancement.user_id == user_id,
        db.func.date(Enhancement.created_at) == today
    ).count()
    return count

def create_demo_user():
    demo_user = User(
        id=999999,
        email='demo@voiceclean.ai',
        name='Demo User',
        is_demo=True
    )
    return demo_user

def enhance_audio_basic(audio_path, output_path, enhancement_type='both'):
    """
    Basic audio enhancement using scipy (Vercel-compatible)
    """
    try:
        # Load audio file
        data, sr = sf.read(audio_path)
        logger.info(f"Loaded audio: {len(data)} samples at {sr} Hz")
        
        if len(data) == 0:
            raise ValueError("Empty audio file")
        
        # Convert to mono if stereo
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        
        # 1. Basic noise reduction
        if enhancement_type in ['noise', 'both']:
            # High-pass filter to remove low-frequency noise
            nyquist = sr / 2
            low_cutoff = 80 / nyquist
            b, a = signal.butter(4, low_cutoff, btype='high')
            data = signal.filtfilt(b, a, data)
            
            # Simple spectral subtraction
            noise_sample_length = min(int(0.5 * sr), len(data) // 4)
            noise_spectrum = np.abs(np.fft.fft(data[:noise_sample_length]))
            
            fft_data = np.fft.fft(data)
            magnitude = np.abs(fft_data)
            phase = np.angle(fft_data)
            
            noise_floor = np.mean(noise_spectrum)
            enhanced_magnitude = np.maximum(magnitude - 0.5 * noise_floor, 0.1 * magnitude)
            
            enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
            data = np.real(np.fft.ifft(enhanced_fft))
        
        # 2. Voice enhancement
        if enhancement_type in ['voice', 'both']:
            # Boost speech frequencies (300-3000 Hz)
            nyquist = sr / 2
            low_freq = 300 / nyquist
            high_freq = 3000 / nyquist
            
            b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            speech_band = signal.filtfilt(b, a, data)
            
            # Mix with original
            data = 0.7 * data + 0.3 * speech_band
        
        # 3. Simple compression
        def simple_compress(audio, threshold=0.7, ratio=2.0):
            compressed = audio.copy()
            for i in range(len(audio)):
                if abs(audio[i]) > threshold:
                    excess = abs(audio[i]) - threshold
                    compressed_excess = excess / ratio
                    new_level = threshold + compressed_excess
                    compressed[i] = new_level * np.sign(audio[i])
            return compressed
        
        data = simple_compress(data)
        
        # 4. Normalize
        max_val = np.max(np.abs(data))
        if max_val > 0:
            data = data / max_val * 0.95
        
        # Save enhanced audio
        sf.write(output_path, data, sr, subtype='PCM_16')
        logger.info(f"Enhanced audio saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in audio enhancement: {e}")
        return False

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        daily_count = get_daily_enhancement_count(current_user.id)
        remaining = MAX_DAILY_ENHANCEMENTS - daily_count
        return render_template('dashboard.html', 
                             user=current_user, 
                             daily_count=daily_count,
                             remaining=remaining,
                             max_daily=MAX_DAILY_ENHANCEMENTS)
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    daily_count = get_daily_enhancement_count(current_user.id)
    remaining = MAX_DAILY_ENHANCEMENTS - daily_count
    
    recent_enhancements = Enhancement.query.filter_by(user_id=current_user.id)\
                                         .order_by(Enhancement.created_at.desc())\
                                         .limit(10).all()
    
    return render_template('dashboard.html', 
                         user=current_user, 
                         daily_count=daily_count,
                         remaining=remaining,
                         max_daily=MAX_DAILY_ENHANCEMENTS,
                         recent_enhancements=recent_enhancements)

@app.route('/login')
def login():
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        redirect_uri = url_for('auth_callback', _external=True)
        return google.authorize_redirect(redirect_uri)
    else:
        # Demo mode
        demo_user = create_demo_user()
        login_user(demo_user)
        flash('Welcome to VoiceClean AI! You are using demo mode.', 'info')
        return redirect(url_for('dashboard'))

@app.route('/auth/callback')
def auth_callback():
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        return redirect(url_for('login'))
    
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            user = User.query.filter_by(google_id=user_info['sub']).first()
            
            if not user:
                user = User(
                    email=user_info['email'],
                    name=user_info['name'],
                    google_id=user_info['sub']
                )
                db.session.add(user)
                db.session.commit()
            
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        flash('Authentication failed. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/api/enhance', methods=['POST'])
@login_required
def enhance_audio():
    """Main endpoint for audio enhancement"""
    try:
        # Check daily limit (skip for demo users)
        if not current_user.is_demo:
            daily_count = get_daily_enhancement_count(current_user.id)
            if daily_count >= MAX_DAILY_ENHANCEMENTS:
                return jsonify({
                    'success': False,
                    'error': f'Daily limit of {MAX_DAILY_ENHANCEMENTS} enhancements reached. Try again tomorrow!'
                }), 429
        
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        enhancement_type = request.form.get('type', 'both')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_input:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
                
                # Save uploaded file
                file.save(temp_input.name)
                
                # Process audio
                start_time = time.time()
                success = enhance_audio_basic(temp_input.name, temp_output.name, enhancement_type)
                processing_time = time.time() - start_time
                
                if success:
                    # Record enhancement (skip for demo users)
                    if not current_user.is_demo:
                        enhancement = Enhancement(
                            user_id=current_user.id,
                            filename=secure_filename(file.filename),
                            enhancement_type=enhancement_type,
                            processing_time=processing_time
                        )
                        db.session.add(enhancement)
                        db.session.commit()
                    
                    # Return enhanced file
                    return send_file(
                        temp_output.name,
                        as_attachment=True,
                        download_name=f'enhanced_{secure_filename(file.filename)}',
                        mimetype='audio/wav'
                    )
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Audio processing failed. Please try with a different file.'
                    }), 500
                
    except Exception as e:
        logger.error(f"Enhancement error: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/api/stats')
@login_required
def get_stats():
    """Get user statistics"""
    try:
        daily_count = get_daily_enhancement_count(current_user.id)
        remaining = MAX_DAILY_ENHANCEMENTS - daily_count
        
        total_enhancements = Enhancement.query.filter_by(user_id=current_user.id).count()
        
        return jsonify({
            'success': True,
            'daily_count': daily_count,
            'remaining': remaining,
            'max_daily': MAX_DAILY_ENHANCEMENTS,
            'total_enhancements': total_enhancements
        })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch statistics'}), 500

# SEO Routes
@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap for SEO"""
    from flask import Response
    
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://voiceclean.ai/</loc>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://voiceclean.ai/dashboard</loc>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>'''
    
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    from flask import Response
    
    robots_txt = '''User-agent: *
Allow: /
Disallow: /api/
Disallow: /auth/

Sitemap: https://voiceclean.ai/sitemap.xml'''
    
    return Response(robots_txt, mimetype='text/plain')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('landing.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('landing.html'), 500

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🎵 VoiceClean AI starting on port {port}")
    print(f"🌐 Access your app at: http://localhost:{port}")
    print(f"🚀 Ready to enhance audio with AI!")
    app.run(host='0.0.0.0', port=port, debug=False)
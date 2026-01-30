from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
import os
import tempfile
import librosa
import soundfile as sf
import numpy as np
import noisereduce as nr
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
    OAUTH_ENABLED = True
else:
    OAUTH_ENABLED = False
    logger.warning("Google OAuth not configured. Running in demo mode.")

# Configuration
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'aac'}
MAX_DAILY_ENHANCEMENTS = int(os.getenv('MAX_DAILY_ENHANCEMENTS', 3))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_demo = db.Column(db.Boolean, default=False)
    
    # Relationships
    enhancements = db.relationship('Enhancement', backref='user', lazy=True)

class Enhancement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    enhancement_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    processing_time = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_daily_enhancement_count(user_id):
    """Get the number of enhancements done today by the user"""
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    
    count = Enhancement.query.filter(
        Enhancement.user_id == user_id,
        Enhancement.created_at >= today,
        Enhancement.created_at < tomorrow
    ).count()
    
    return count

def create_demo_user():
    """Create a demo user for testing without OAuth"""
    demo_user = User(
        email='demo@voiceclean.ai',
        name='Demo User',
        picture='',
        is_demo=True
    )
    db.session.add(demo_user)
    db.session.commit()
    return demo_user

def enhance_audio_advanced(audio_path, output_path, enhancement_type='both'):
    """
    Advanced audio enhancement using multiple techniques
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_path, sr=None)
        logger.info(f"Loaded audio: {len(y)} samples at {sr} Hz")
        
        if len(y) == 0:
            raise ValueError("Empty audio file")
        
        original_y = y.copy()
        
        # 1. Noise reduction using noisereduce library
        if enhancement_type in ['noise', 'both']:
            # Use noisereduce for better noise reduction
            y = nr.reduce_noise(y=y, sr=sr, stationary=True, prop_decrease=0.8)
            
            # Additional spectral gating
            stft = librosa.stft(y, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Adaptive noise floor estimation
            noise_floor = np.percentile(magnitude, 10)
            gate_threshold = noise_floor * 4
            
            # Soft gating with smooth transitions
            mask = magnitude / (magnitude + gate_threshold)
            enhanced_magnitude = magnitude * mask
            
            # Reconstruct
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            y = librosa.istft(enhanced_stft, hop_length=512)
        
        # 2. Voice enhancement
        if enhancement_type in ['voice', 'both']:
            # Multi-band processing
            from scipy.signal import butter, filtfilt
            
            # High-pass filter to remove low-frequency noise
            nyquist = sr / 2
            low_cutoff = 85 / nyquist
            b, a = butter(6, low_cutoff, btype='high')
            y = filtfilt(b, a, y)
            
            # Enhance speech frequencies with EQ
            stft = librosa.stft(y, n_fft=2048, hop_length=512)
            freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
            
            # Create sophisticated frequency response
            gain = np.ones_like(freqs)
            
            # Boost fundamental speech frequencies (200-800 Hz)
            fundamental_mask = (freqs >= 200) & (freqs <= 800)
            gain[fundamental_mask] = 1.4
            
            # Boost consonant clarity (2000-4000 Hz)
            consonant_mask = (freqs >= 2000) & (freqs <= 4000)
            gain[consonant_mask] = 1.3
            
            # Slight boost for presence (4000-8000 Hz)
            presence_mask = (freqs >= 4000) & (freqs <= 8000)
            gain[presence_mask] = 1.1
            
            # Apply frequency-dependent gain
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            enhanced_magnitude = magnitude * gain[:, np.newaxis]
            
            # Reconstruct
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            y = librosa.istft(enhanced_stft, hop_length=512)
        
        # 3. Dynamic range processing
        def soft_compress(audio, threshold=0.6, ratio=3.0, attack=0.003, release=0.1):
            compressed = audio.copy()
            envelope = 0.0
            
            for i in range(len(audio)):
                input_level = abs(audio[i])
                
                # Envelope follower
                if input_level > envelope:
                    envelope += (input_level - envelope) * attack
                else:
                    envelope += (input_level - envelope) * release
                
                # Apply compression
                if envelope > threshold:
                    excess = envelope - threshold
                    compressed_excess = excess / ratio
                    gain = (threshold + compressed_excess) / envelope if envelope > 0 else 1
                    compressed[i] = audio[i] * gain
            
            return compressed
        
        y = soft_compress(y)
        
        # 4. Harmonic enhancement for voice clarity
        if enhancement_type in ['voice', 'both']:
            # Subtle harmonic excitation
            harmonics = librosa.effects.harmonic(y)
            y = 0.85 * y + 0.15 * harmonics
        
        # 5. Final normalization and limiting
        # Normalize to prevent clipping
        max_val = np.max(np.abs(y))
        if max_val > 0:
            y = y / max_val * 0.95
        
        # Soft limiting
        y = np.tanh(y * 1.2) * 0.9
        
        # Save enhanced audio
        sf.write(output_path, y, sr, subtype='PCM_16')
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
    return render_template('landing.html', oauth_enabled=OAUTH_ENABLED)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if not OAUTH_ENABLED:
        # Demo mode - create or login demo user
        demo_user = User.query.filter_by(email='demo@voiceclean.ai').first()
        if not demo_user:
            demo_user = create_demo_user()
        login_user(demo_user)
        return redirect(url_for('index'))
    
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    if not OAUTH_ENABLED:
        return redirect(url_for('login'))
    
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info:
        user = User.query.filter_by(google_id=user_info['sub']).first()
        
        if not user:
            user = User(
                google_id=user_info['sub'],
                email=user_info['email'],
                name=user_info['name'],
                picture=user_info.get('picture', '')
            )
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    flash('Authentication failed. Please try again.', 'error')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
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
                    'error': f'Daily limit reached. You can enhance {MAX_DAILY_ENHANCEMENTS} files per day.',
                    'daily_count': daily_count,
                    'max_daily': MAX_DAILY_ENHANCEMENTS
                }), 429
        
        # Validate request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(audio_file.filename):
            return jsonify({'error': 'Invalid file type. Supported: WAV, MP3, M4A, FLAC, OGG, AAC'}), 400
        
        # Get enhancement options
        enhancement_type = request.form.get('type', 'both')
        if enhancement_type not in ['noise', 'voice', 'both']:
            enhancement_type = 'both'
        
        # Secure filename
        filename = secure_filename(audio_file.filename)
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_input:
            audio_file.save(temp_input.name)
            file_size = os.path.getsize(temp_input.name)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
                start_time = time.time()
                
                # Enhance the audio
                success = enhance_audio_advanced(temp_input.name, temp_output.name, enhancement_type)
                
                processing_time = time.time() - start_time
                logger.info(f"Audio processing completed in {processing_time:.2f} seconds")
                
                if success:
                    # Record the enhancement
                    enhancement = Enhancement(
                        user_id=current_user.id,
                        filename=filename,
                        enhancement_type=enhancement_type,
                        file_size=file_size,
                        processing_time=processing_time
                    )
                    db.session.add(enhancement)
                    db.session.commit()
                    
                    # Return the enhanced audio file
                    return send_file(
                        temp_output.name,
                        as_attachment=True,
                        download_name=f"enhanced_{filename}",
                        mimetype='audio/wav'
                    )
                else:
                    return jsonify({'error': 'Audio enhancement failed'}), 500
    
    except Exception as e:
        logger.error(f"Error in enhance_audio endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        # Clean up temporary files
        try:
            if 'temp_input' in locals():
                os.unlink(temp_input.name)
            if 'temp_output' in locals():
                os.unlink(temp_output.name)
        except:
            pass

@app.route('/api/usage')
@login_required
def get_usage():
    """Get user's usage statistics"""
    daily_count = get_daily_enhancement_count(current_user.id)
    total_count = Enhancement.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'daily_count': daily_count,
        'remaining': MAX_DAILY_ENHANCEMENTS - daily_count if not current_user.is_demo else 999,
        'max_daily': MAX_DAILY_ENHANCEMENTS,
        'total_count': total_count,
        'is_demo': current_user.is_demo
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'features': ['noise_reduction', 'voice_enhancement', 'google_auth', 'usage_limits'],
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'oauth_enabled': OAUTH_ENABLED
    })

# SEO Routes
@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap for SEO"""
    from flask import Response
    
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://voiceclean.ai/</loc>
        <lastmod>2024-01-30</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://voiceclean.ai/login</loc>
        <lastmod>2024-01-30</lastmod>
        <changefreq>monthly</changefreq>
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

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': f'File too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the app on port 3000
    port = int(os.environ.get('PORT', 3000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 VoiceClean AI - Professional SaaS Starting...")
    print(f"🌐 NEW HOST: http://localhost:{port}")
    print("🎯 Complete Audio Enhancement Platform")
    print("✨ Google OAuth + AI Processing + Usage Limits")
    print("💰 AdSense Ready + SEO Optimized")
    print("📱 Mobile Responsive + Production Ready")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
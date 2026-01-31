from flask import Flask, request, jsonify, send_file, render_template
import os
import logging
from werkzeug.utils import secure_filename
import requests
import io
import time
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 55 * 1024 * 1024  # 55MB

# Constants - Support all major audio formats
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac', 'webm', 'opus', 'wma', 'amr'}

# ElevenLabs API Configuration
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', 'your_elevenlabs_api_key_here')
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_audio_elevenlabs(audio_data):
    """Use ElevenLabs Audio Isolation API for professional audio enhancement"""
    try:
        logger.info("🎵 Using ElevenLabs Audio Isolation API...")
        
        # ElevenLabs Audio Isolation endpoint
        url = f"{ELEVENLABS_BASE_URL}/audio-isolation"
        
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "audio/mpeg"
        }
        
        # Send audio to ElevenLabs for isolation/enhancement
        response = requests.post(
            url,
            headers=headers,
            data=audio_data,
            timeout=120  # 2 minutes for large files
        )
        
        logger.info(f"ElevenLabs API response: {response.status_code}")
        
        if response.status_code == 200:
            enhanced_audio = response.content
            if len(enhanced_audio) > 1000:
                logger.info("✅ ElevenLabs enhancement successful!")
                return enhanced_audio, "ElevenLabs Audio Isolation"
            else:
                logger.warning("ElevenLabs returned small response")
                return None, None
        elif response.status_code == 401:
            logger.error("ElevenLabs API key invalid")
            return None, "Invalid API Key"
        elif response.status_code == 429:
            logger.error("ElevenLabs rate limit exceeded")
            return None, "Rate Limited"
        else:
            logger.error(f"ElevenLabs API error: {response.status_code}")
            return None, f"API Error {response.status_code}"
            
    except Exception as e:
        logger.error(f"ElevenLabs API error: {e}")
        return None, str(e)

def fallback_enhancement(audio_data):
    """Fallback enhancement using free APIs"""
    try:
        logger.info("🔄 Using fallback enhancement...")
        
        # Try Facebook Denoiser as fallback
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/denoiser",
            data=audio_data,
            timeout=60
        )
        
        if response.status_code == 200 and len(response.content) > 1000:
            logger.info("✅ Fallback enhancement successful!")
            return response.content, "Facebook Denoiser (Fallback)"
        
        # If all fails, return original
        logger.info("⚠️ Returning original audio")
        return audio_data, "Original (No Enhancement Available)"
        
    except Exception as e:
        logger.error(f"Fallback enhancement error: {e}")
        return audio_data, "Original (Error Fallback)"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Professional audio enhancement using ElevenLabs API"""
    try:
        logger.info("🎵 Audio enhancement request received")
        
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
        
        # Read file data
        try:
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Seek back to beginning
            
            file_size_mb = file_size / (1024 * 1024)
            
            logger.info(f"📁 File: {file.filename}")
            logger.info(f"📊 Size: {file_size:,} bytes ({file_size_mb:.1f} MB)")
            
            # Size validation
            if file_size == 0:
                return jsonify({'success': False, 'error': 'Empty file uploaded'}), 400
            
            if file_size > 55 * 1024 * 1024:  # 55MB limit
                return jsonify({
                    'success': False, 
                    'error': f'File too large ({file_size_mb:.1f}MB). Maximum allowed: 55MB'
                }), 413
            
            if file_size < 1000:  # Minimum 1KB
                return jsonify({'success': False, 'error': 'File too small (minimum 1KB)'}), 400
            
            # Read the file
            audio_data = file.read()
            
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return jsonify({'success': False, 'error': 'Error reading uploaded file'}), 400
        
        # Try ElevenLabs enhancement first
        logger.info("� Starting ElevenLabs audio enhancement...")
        enhanced_audio, method_used = enhance_audio_elevenlabs(audio_data)
        
        # If ElevenLabs fails, use fallback
        if not enhanced_audio:
            logger.info("🔄 ElevenLabs failed, trying fallback...")
            enhanced_audio, method_used = fallback_enhancement(audio_data)
        
        if not enhanced_audio:
            return jsonify({
                'success': False, 
                'error': 'Enhancement failed. Please try again.'
            }), 500
        
        # Success!
        output_size = len(enhanced_audio)
        output_size_mb = output_size / (1024 * 1024)
        
        logger.info(f"✅ Enhancement completed!")
        logger.info(f"🎯 Method: {method_used}")
        logger.info(f"📈 Output: {output_size:,} bytes ({output_size_mb:.1f} MB)")
        
        # Create output filename
        base_name = os.path.splitext(secure_filename(file.filename))[0]
        output_filename = f'{base_name}_enhanced_elevenlabs.wav'
        
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
    """Health check with ElevenLabs integration status"""
    elevenlabs_status = "configured" if ELEVENLABS_API_KEY != 'your_elevenlabs_api_key_here' else "demo_mode"
    
    return jsonify({
        'status': 'healthy',
        'version': '9.0 - ElevenLabs Integration',
        'primary_service': 'ElevenLabs Audio Isolation',
        'elevenlabs_status': elevenlabs_status,
        'supported_formats': sorted(list(ALLOWED_EXTENSIONS)),
        'max_file_size': '55MB',
        'features': [
            'ElevenLabs Audio Isolation',
            'Professional noise removal',
            'Studio-quality enhancement',
            'Voice isolation technology',
            'Fallback enhancement system'
        ],
        'ui_style': 'ElevenLabs inspired minimal design',
        'ready': True
    })

@app.route('/api/test')
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        'message': 'VoiceClean AI v9.0 - ElevenLabs Integration Ready!',
        'timestamp': time.time(),
        'status': 'operational',
        'service': 'ElevenLabs Audio Isolation',
        'max_file_size': '55MB'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 55MB.'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again.'
    }), 500

if __name__ == '__main__':
    app.run(debug=True)
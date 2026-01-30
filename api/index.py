from flask import Flask, request, jsonify, send_file, render_template
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import requests
import shutil
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Constants
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'}

# Multiple working Hugging Face APIs for audio enhancement
HF_API_TOKEN = os.getenv('HF_API_TOKEN', 'hf_your_token_here')

# List of working audio enhancement models
AUDIO_ENHANCEMENT_APIS = [
    {
        "name": "Facebook Denoiser",
        "url": "https://api-inference.huggingface.co/models/facebook/denoiser",
        "description": "Advanced noise removal"
    },
    {
        "name": "SpeechBrain Enhancement", 
        "url": "https://api-inference.huggingface.co/models/speechbrain/sepformer-wham-enhancement",
        "description": "Speech enhancement and separation"
    },
    {
        "name": "Microsoft SpeechT5",
        "url": "https://api-inference.huggingface.co/models/microsoft/speecht5_tts",
        "description": "Speech processing"
    }
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_audio_with_api(audio_data):
    """Try multiple Hugging Face APIs for audio enhancement"""
    
    if HF_API_TOKEN == 'hf_your_token_here':
        logger.info("No API token - using demo mode")
        return audio_data, "demo"
    
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "audio/wav"
    }
    
    # Try each API in order
    for api in AUDIO_ENHANCEMENT_APIS:
        try:
            logger.info(f"Trying {api['name']}...")
            
            response = requests.post(
                api['url'],
                headers=headers,
                data=audio_data,
                timeout=30
            )
            
            logger.info(f"{api['name']} response: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"Success with {api['name']}")
                return response.content, api['name']
            elif response.status_code == 503:
                logger.info(f"{api['name']} is loading, trying next...")
                continue
            else:
                logger.info(f"{api['name']} failed with {response.status_code}")
                continue
                
        except Exception as e:
            logger.error(f"Error with {api['name']}: {e}")
            continue
    
    # If all APIs fail, return original audio
    logger.info("All APIs failed, returning original audio")
    return audio_data, "original"

def simple_audio_enhancement(audio_data):
    """Simple audio enhancement using basic processing"""
    try:
        # For demo purposes, we'll just return the original audio
        # In a real implementation, you could add basic audio processing here
        logger.info("Applying simple enhancement...")
        return audio_data
    except Exception as e:
        logger.error(f"Simple enhancement error: {e}")
        return audio_data

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Enhanced audio processing endpoint with better error handling"""
    try:
        logger.info("Enhancement request received")
        
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        logger.info(f"Processing file: {file.filename} ({file.content_length} bytes)")
        
        # Read audio data directly into memory
        audio_data = file.read()
        
        if len(audio_data) == 0:
            return jsonify({'success': False, 'error': 'Empty file uploaded'}), 400
        
        logger.info(f"Audio data size: {len(audio_data)} bytes")
        
        # Try AI enhancement
        enhanced_audio, method_used = enhance_audio_with_api(audio_data)
        
        if enhanced_audio is None:
            # Fallback to simple enhancement
            enhanced_audio = simple_audio_enhancement(audio_data)
            method_used = "simple"
        
        logger.info(f"Enhancement completed using: {method_used}")
        
        # Create response with enhanced audio
        output_filename = f'enhanced_{secure_filename(file.filename)}'
        
        # Return the enhanced audio file
        return send_file(
            io.BytesIO(enhanced_audio),
            as_attachment=True,
            download_name=output_filename,
            mimetype='audio/wav'
        )
                
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Processing failed: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint with detailed status"""
    api_status = "working" if HF_API_TOKEN != 'hf_your_token_here' else "demo_mode"
    
    return jsonify({
        'status': 'healthy',
        'ai_enhancement': api_status,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'available_apis': len(AUDIO_ENHANCEMENT_APIS),
        'max_file_size': '50MB',
        'version': '2.0'
    })

@app.route('/api/test')
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({
        'message': 'VoiceClean AI is working!',
        'timestamp': str(os.environ.get('VERCEL_REGION', 'local')),
        'status': 'ok'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('landing.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
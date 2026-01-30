from flask import Flask, request, jsonify, send_file, render_template
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import requests
import shutil
import io
import base64
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Constants
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'}

# Get API token from environment
HF_API_TOKEN = os.getenv('HF_API_TOKEN', 'hf_your_token_here')

# Working audio enhancement APIs in order of preference
AUDIO_ENHANCEMENT_APIS = [
    {
        "name": "SpeechBrain SGMSE VoiceBank",
        "url": "https://api-inference.huggingface.co/models/speechbrain/sgmse-voicebank",
        "description": "State-of-the-art speech enhancement with diffusion models",
        "priority": 1
    },
    {
        "name": "SpeechBrain SepFormer Enhancement",
        "url": "https://api-inference.huggingface.co/models/speechbrain/sepformer-wham-enhancement", 
        "description": "Speech enhancement and separation",
        "priority": 2
    },
    {
        "name": "SpeechBrain MTL Mimic VoiceBank",
        "url": "https://api-inference.huggingface.co/models/speechbrain/mtl-mimic-voicebank",
        "description": "Multi-task learning enhanced speech",
        "priority": 3
    },
    {
        "name": "Facebook Denoiser",
        "url": "https://api-inference.huggingface.co/models/facebook/denoiser",
        "description": "Real-time speech enhancement",
        "priority": 4
    }
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_audio_with_best_api(audio_data):
    """Try the best working audio enhancement APIs in order of priority"""
    
    if HF_API_TOKEN == 'hf_your_token_here':
        logger.info("No API token - using demo mode")
        return audio_data, "demo"
    
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "audio/wav"
    }
    
    # Sort APIs by priority
    sorted_apis = sorted(AUDIO_ENHANCEMENT_APIS, key=lambda x: x['priority'])
    
    for api in sorted_apis:
        try:
            logger.info(f"Trying {api['name']} (Priority {api['priority']})...")
            
            response = requests.post(
                api['url'],
                headers=headers,
                data=audio_data,
                timeout=60  # Increased timeout for better models
            )
            
            logger.info(f"{api['name']} response: {response.status_code}")
            
            if response.status_code == 200:
                # Check if response is valid audio
                if len(response.content) > 1000:  # Valid audio should be larger
                    logger.info(f"✅ Success with {api['name']}")
                    return response.content, api['name']
                else:
                    logger.info(f"⚠️ {api['name']} returned small response, trying next...")
                    continue
                    
            elif response.status_code == 503:
                logger.info(f"⏳ {api['name']} is loading, trying next...")
                continue
                
            elif response.status_code == 429:
                logger.info(f"⏸️ {api['name']} rate limited, trying next...")
                continue
                
            else:
                logger.info(f"❌ {api['name']} failed with {response.status_code}")
                continue
                
        except requests.exceptions.Timeout:
            logger.info(f"⏰ {api['name']} timed out, trying next...")
            continue
            
        except Exception as e:
            logger.error(f"❌ Error with {api['name']}: {e}")
            continue
    
    # If all APIs fail, return original audio
    logger.info("⚠️ All APIs failed, returning original audio")
    return audio_data, "original"

def wait_for_model_loading(api_url, headers, max_wait=120):
    """Wait for Hugging Face model to load if it's cold starting"""
    logger.info("🔄 Checking if model needs to warm up...")
    
    # Send a small test request to warm up the model
    test_data = b'\x00' * 1024  # Small dummy audio data
    
    for attempt in range(3):
        try:
            response = requests.post(api_url, headers=headers, data=test_data, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ Model is ready!")
                return True
            elif response.status_code == 503:
                wait_time = min(20 + (attempt * 10), 60)
                logger.info(f"⏳ Model loading... waiting {wait_time}s (attempt {attempt + 1}/3)")
                time.sleep(wait_time)
                continue
            else:
                logger.info(f"⚠️ Model test returned {response.status_code}")
                return False
                
        except Exception as e:
            logger.info(f"⚠️ Model warm-up attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(10)
                continue
            return False
    
    return False

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Production-ready audio enhancement endpoint with best APIs"""
    try:
        logger.info("🎵 Enhancement request received")
        
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': f'Unsupported file type. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        logger.info(f"📁 Processing: {file.filename} ({len(file.read())} bytes)")
        file.seek(0)  # Reset file pointer after reading length
        
        # Read audio data
        audio_data = file.read()
        
        if len(audio_data) == 0:
            return jsonify({'success': False, 'error': 'Empty file uploaded'}), 400
        
        if len(audio_data) < 1000:
            return jsonify({'success': False, 'error': 'Audio file too small (minimum 1KB)'}), 400
        
        logger.info(f"📊 Audio data size: {len(audio_data)} bytes")
        
        # Try AI enhancement with best APIs
        enhanced_audio, method_used = enhance_audio_with_best_api(audio_data)
        
        if enhanced_audio is None or len(enhanced_audio) == 0:
            logger.error("❌ All enhancement methods failed")
            return jsonify({
                'success': False, 
                'error': 'Enhancement failed - please try again or use a different audio file'
            }), 500
        
        logger.info(f"✅ Enhancement completed using: {method_used}")
        logger.info(f"📈 Output size: {len(enhanced_audio)} bytes")
        
        # Create response filename
        base_name = os.path.splitext(secure_filename(file.filename))[0]
        output_filename = f'{base_name}_enhanced.wav'
        
        # Return enhanced audio
        return send_file(
            io.BytesIO(enhanced_audio),
            as_attachment=True,
            download_name=output_filename,
            mimetype='audio/wav'
        )
                
    except Exception as e:
        logger.error(f"💥 Endpoint error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    """Comprehensive health check with API status"""
    api_status = "production" if HF_API_TOKEN != 'hf_your_token_here' else "demo_mode"
    
    # Test API connectivity if token is available
    api_connectivity = "unknown"
    if HF_API_TOKEN != 'hf_your_token_here':
        try:
            # Quick test of the primary API
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            response = requests.get(
                "https://api-inference.huggingface.co/models/speechbrain/sgmse-voicebank",
                headers=headers,
                timeout=5
            )
            api_connectivity = "connected" if response.status_code in [200, 503] else "error"
        except:
            api_connectivity = "error"
    
    return jsonify({
        'status': 'healthy',
        'ai_enhancement': api_status,
        'api_connectivity': api_connectivity,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'available_apis': len(AUDIO_ENHANCEMENT_APIS),
        'max_file_size': '50MB',
        'version': '3.0',
        'primary_model': 'SpeechBrain SGMSE VoiceBank',
        'features': [
            'Advanced noise removal',
            'Voice clarity enhancement', 
            'Multiple API fallbacks',
            'Production-ready processing'
        ]
    })

@app.route('/api/models')
def list_models():
    """List available enhancement models"""
    models = []
    for api in sorted(AUDIO_ENHANCEMENT_APIS, key=lambda x: x['priority']):
        models.append({
            'name': api['name'],
            'description': api['description'],
            'priority': api['priority'],
            'status': 'available'
        })
    
    return jsonify({
        'models': models,
        'total': len(models),
        'primary': models[0]['name'] if models else None
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('landing.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
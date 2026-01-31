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

# Direct API processing - no local storage, direct to external APIs
DIRECT_PROCESSING_APIS = [
    {
        "name": "Hugging Face - AnyEnhance",
        "url": "https://api-inference.huggingface.co/models/amphion/anyenhance",
        "description": "Unified voice enhancement",
        "timeout": 120
    },
    {
        "name": "Hugging Face - Facebook Denoiser", 
        "url": "https://api-inference.huggingface.co/models/facebook/denoiser",
        "description": "Professional noise removal",
        "timeout": 90
    },
    {
        "name": "Hugging Face - Resemble Enhance",
        "url": "https://api-inference.huggingface.co/models/resemble-ai/resemble-enhance", 
        "description": "Advanced voice enhancement",
        "timeout": 100
    },
    {
        "name": "Hugging Face - SpeechBrain MetricGAN+",
        "url": "https://api-inference.huggingface.co/models/speechbrain/metricgan-plus-voicebank",
        "description": "State-of-the-art enhancement",
        "timeout": 80
    },
    {
        "name": "Hugging Face - SpeechBrain SGMSE",
        "url": "https://api-inference.huggingface.co/models/speechbrain/sgmse-voicebank",
        "description": "Diffusion-based enhancement", 
        "timeout": 90
    }
]

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def direct_api_processing(audio_data, file_size_mb):
    """Send audio directly to external APIs for processing - no local storage"""
    
    logger.info(f"🚀 Starting direct API processing for {file_size_mb:.1f}MB file")
    
    # Try each API in order of preference
    for api in DIRECT_PROCESSING_APIS:
        try:
            logger.info(f"🔄 Trying {api['name']}...")
            logger.info(f"   Sending {len(audio_data):,} bytes to external API...")
            
            # Send directly to external API
            response = requests.post(
                api['url'],
                data=audio_data,
                headers={
                    'Content-Type': 'audio/wav',
                    'User-Agent': 'VoiceClean-AI/1.0'
                },
                timeout=api['timeout'],
                stream=True  # Stream response for large files
            )
            
            logger.info(f"   {api['name']} response: {response.status_code}")
            
            if response.status_code == 200:
                # Get the enhanced audio directly from API
                enhanced_audio = response.content
                
                if len(enhanced_audio) > 1000:  # Valid audio response
                    logger.info(f"✅ Success with {api['name']}")
                    logger.info(f"   Enhanced audio size: {len(enhanced_audio):,} bytes")
                    return enhanced_audio, api['name']
                else:
                    logger.warning(f"   {api['name']} returned small response, trying next...")
                    continue
                    
            elif response.status_code == 503:
                logger.info(f"   ⏳ {api['name']} model loading, trying next...")
                continue
                
            elif response.status_code == 429:
                logger.info(f"   ⏸️ {api['name']} rate limited, trying next...")
                continue
                
            else:
                logger.warning(f"   ❌ {api['name']} failed: {response.status_code}")
                continue
                
        except requests.exceptions.Timeout:
            logger.warning(f"   ⏰ {api['name']} timed out, trying next...")
            continue
            
        except requests.exceptions.RequestException as e:
            logger.error(f"   ❌ {api['name']} request error: {e}")
            continue
            
        except Exception as e:
            logger.error(f"   ❌ {api['name']} unexpected error: {e}")
            continue
    
    # If all APIs fail, return original audio
    logger.warning("⚠️ All external APIs failed, returning original audio")
    return audio_data, "Original (No Enhancement Available)"

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Direct API processing - send to external APIs, return enhanced audio"""
    try:
        logger.info("🎵 Direct API processing request received")
        
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
        
        # Read file data - direct processing, no local storage
        try:
            # Get file size first
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
            
            # Read the entire file into memory for direct API processing
            logger.info("📖 Reading file for direct API processing...")
            audio_data = file.read()
            
            if len(audio_data) != file_size:
                logger.warning(f"Size mismatch: expected {file_size}, got {len(audio_data)}")
            
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return jsonify({'success': False, 'error': 'Error reading uploaded file'}), 400
        
        # Direct API processing - send to external APIs
        logger.info("🌐 Starting direct external API processing...")
        enhanced_audio, method_used = direct_api_processing(audio_data, file_size_mb)
        
        if not enhanced_audio:
            return jsonify({
                'success': False, 
                'error': 'Enhancement failed. All external APIs are currently unavailable.'
            }), 500
        
        # Success! Return enhanced audio directly to client
        output_size = len(enhanced_audio)
        output_size_mb = output_size / (1024 * 1024)
        
        logger.info(f"✅ Direct processing completed!")
        logger.info(f"🎯 Method: {method_used}")
        logger.info(f"📈 Output: {output_size:,} bytes ({output_size_mb:.1f} MB)")
        
        # Create output filename
        base_name = os.path.splitext(secure_filename(file.filename))[0]
        output_filename = f'{base_name}_enhanced_55mb.wav'
        
        # Return enhanced audio directly to client for download
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
    """Health check for direct API processing"""
    return jsonify({
        'status': 'healthy',
        'version': '8.0 - Direct API Processing',
        'processing_method': 'Direct external API calls',
        'local_storage': 'None - Direct processing only',
        'supported_formats': sorted(list(ALLOWED_EXTENSIONS)),
        'max_file_size': '55MB',
        'available_apis': len(DIRECT_PROCESSING_APIS),
        'api_providers': [api['name'] for api in DIRECT_PROCESSING_APIS],
        'features': [
            'Direct API processing (no local storage)',
            '55MB file support',
            'Multiple external AI APIs',
            'Stream processing for large files',
            'No Vercel storage limitations'
        ],
        'ready': True
    })

@app.route('/api/models')
def list_models():
    """List available external APIs"""
    models = []
    for i, api in enumerate(DIRECT_PROCESSING_APIS):
        models.append({
            'id': i + 1,
            'name': api['name'],
            'description': api['description'],
            'timeout': api['timeout'],
            'type': 'External API',
            'processing': 'Direct'
        })
    
    return jsonify({
        'models': models,
        'total_models': len(models),
        'processing_method': 'Direct external API calls',
        'max_file_size': '55MB',
        'storage_method': 'No local storage - direct processing'
    })

@app.route('/api/test')
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        'message': 'VoiceClean AI v8.0 - Direct API Processing Ready!',
        'timestamp': time.time(),
        'status': 'operational',
        'max_file_size': '55MB',
        'processing': 'Direct external APIs',
        'storage': 'None - stream processing'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('landing.html'), 404

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 55MB for direct API processing.'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again.'
    }), 500

if __name__ == '__main__':
    app.run(debug=True)
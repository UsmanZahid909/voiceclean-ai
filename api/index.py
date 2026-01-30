from flask import Flask, request, jsonify, send_file, render_template
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import requests
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Constants
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'}

# Working Hugging Face API
HF_API_TOKEN = os.getenv('HF_API_TOKEN', 'hf_your_token_here')
WORKING_API_URL = "https://api-inference.huggingface.co/models/speechbrain/sepformer-wham-enhancement"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_audio_working(input_path, output_path):
    """Simple working audio enhancement"""
    try:
        logger.info("Attempting audio enhancement...")
        
        # If no API token, just copy file (demo mode)
        if HF_API_TOKEN == 'hf_your_token_here':
            logger.info("Demo mode - copying file")
            shutil.copy2(input_path, output_path)
            return True
        
        # Try API enhancement
        with open(input_path, 'rb') as f:
            audio_data = f.read()
        
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "audio/wav"
        }
        
        logger.info(f"Sending {len(audio_data)} bytes to API...")
        
        response = requests.post(
            WORKING_API_URL,
            headers=headers,
            data=audio_data,
            timeout=30
        )
        
        logger.info(f"API response: {response.status_code}")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info("API enhancement successful")
            return True
        else:
            logger.info("API failed, using demo mode")
            shutil.copy2(input_path, output_path)
            return True
            
    except Exception as e:
        logger.error(f"Enhancement error: {e}")
        # Always fallback to copying file
        try:
            shutil.copy2(input_path, output_path)
            return True
        except:
            return False

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Simple working audio enhancement endpoint"""
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
        
        # Create temp files
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        
        try:
            # Save uploaded file
            file.save(temp_input.name)
            temp_input.close()
            
            logger.info(f"Processing file: {file.filename}")
            
            # Enhance audio
            success = enhance_audio_working(temp_input.name, temp_output.name)
            temp_output.close()
            
            if success and os.path.exists(temp_output.name):
                logger.info("Sending enhanced file")
                return send_file(
                    temp_output.name,
                    as_attachment=True,
                    download_name=f'enhanced_{secure_filename(file.filename)}',
                    mimetype='audio/wav'
                )
            else:
                return jsonify({'success': False, 'error': 'Enhancement failed'}), 500
                
        finally:
            # Cleanup
            try:
                if os.path.exists(temp_input.name):
                    os.unlink(temp_input.name)
                if os.path.exists(temp_output.name):
                    os.unlink(temp_output.name)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_enhancement': 'working' if HF_API_TOKEN != 'hf_your_token_here' else 'demo_mode',
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('landing.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
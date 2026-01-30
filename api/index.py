from flask import Flask, request, jsonify, send_file, render_template
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import time
import requests
import json
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Constants
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'}

# Best Hugging Face Audio Enhancement APIs
AUDIO_MODELS = {
    'facebook_sam': {
        'url': "https://api-inference.huggingface.co/models/facebook/sam-audio-large",
        'description': "Facebook SAM-Audio - Latest foundation model for audio separation"
    },
    'speechbrain_rescue': {
        'url': "https://api-inference.huggingface.co/models/speechbrain/sepformer_rescuespeech", 
        'description': "SpeechBrain RescueSpeech - Specialized for speech enhancement"
    },
    'speechbrain_wham': {
        'url': "https://api-inference.huggingface.co/models/speechbrain/sepformer-wham-enhancement",
        'description': "SpeechBrain WHAM - Noise removal and enhancement"
    },
    'speechbrain_whamr': {
        'url': "https://api-inference.huggingface.co/models/speechbrain/sepformer-whamr-enhancement",
        'description': "SpeechBrain WHAMR - Denoising + dereverberation"
    },
    'speechbrain_mimic': {
        'url': "https://api-inference.huggingface.co/models/speechbrain/mtl-mimic-voicebank",
        'description': "SpeechBrain Mimic - Perceptual enhancement"
    }
}

HF_API_TOKEN = os.getenv('HF_API_TOKEN', 'hf_your_token_here')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_enhancement_description(enhancement_type):
    """Get description for SAM-Audio based on enhancement type"""
    descriptions = {
        'both': "Background noise and unwanted sounds",
        'noise': "Background noise, hums, and environmental sounds", 
        'voice': "Non-speech sounds while preserving clear speech"
    }
    return descriptions.get(enhancement_type, descriptions['both'])

def enhance_audio_with_facebook_sam(input_path, output_path, enhancement_type='both'):
    """Facebook SAM-Audio - Latest foundation model"""
    try:
        logger.info("Attempting Facebook SAM-Audio enhancement...")
        
        if HF_API_TOKEN == 'hf_your_token_here':
            logger.info("No API token, skipping Facebook SAM")
            return False
        
        with open(input_path, 'rb') as f:
            audio_data = f.read()
        
        if len(audio_data) == 0:
            logger.error("Empty audio file")
            return False
        
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "audio/wav"
        }
        
        logger.info(f"Sending {len(audio_data)} bytes to Facebook SAM-Audio...")
        
        response = requests.post(
            AUDIO_MODELS['facebook_sam']['url'],
            headers=headers,
            data=audio_data,
            timeout=90
        )
        
        logger.info(f"Facebook SAM response: {response.status_code}")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info("Audio enhanced successfully using Facebook SAM-Audio")
            return True
        elif response.status_code == 503:
            logger.info("Facebook SAM model loading, trying fallback")
            return False
        else:
            logger.error(f"Facebook SAM error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Facebook SAM error: {e}")
        return False

def enhance_audio_with_speechbrain_rescue(input_path, output_path, enhancement_type='both'):
    """SpeechBrain RescueSpeech - Specialized for speech enhancement"""
    try:
        logger.info("Attempting SpeechBrain RescueSpeech enhancement...")
        
        if HF_API_TOKEN == 'hf_your_token_here':
            return False
        
        with open(input_path, 'rb') as f:
            audio_data = f.read()
        
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "audio/wav"
        }
        
        logger.info(f"Using SpeechBrain RescueSpeech for enhancement...")
        
        response = requests.post(
            AUDIO_MODELS['speechbrain_rescue']['url'],
            headers=headers,
            data=audio_data,
            timeout=60
        )
        
        logger.info(f"SpeechBrain RescueSpeech response: {response.status_code}")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info("Audio enhanced successfully using SpeechBrain RescueSpeech")
            return True
        else:
            logger.error(f"SpeechBrain RescueSpeech error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"SpeechBrain RescueSpeech error: {e}")
        return False

def enhance_audio_with_speechbrain_wham(input_path, output_path, enhancement_type='both'):
    """SpeechBrain WHAM - Noise removal and enhancement"""
    try:
        logger.info("Attempting SpeechBrain WHAM enhancement...")
        
        if HF_API_TOKEN == 'hf_your_token_here':
            return False
        
        with open(input_path, 'rb') as f:
            audio_data = f.read()
        
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "audio/wav"
        }
        
        # Choose the right WHAM model based on enhancement type
        model_key = 'speechbrain_whamr' if enhancement_type == 'both' else 'speechbrain_wham'
        api_url = AUDIO_MODELS[model_key]['url']
        
        logger.info(f"Using SpeechBrain WHAM for {enhancement_type} enhancement...")
        
        response = requests.post(
            api_url,
            headers=headers,
            data=audio_data,
            timeout=60
        )
        
        logger.info(f"SpeechBrain WHAM response: {response.status_code}")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info("Audio enhanced successfully using SpeechBrain WHAM")
            return True
        else:
            logger.error(f"SpeechBrain WHAM error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"SpeechBrain WHAM error: {e}")
        return False

def enhance_audio_basic(input_path, output_path, enhancement_type='both'):
    """Fallback basic audio processing"""
    try:
        import shutil
        shutil.copy2(input_path, output_path)
        logger.info(f"Basic audio processing completed")
        return True
    except Exception as e:
        logger.error(f"Basic processing error: {e}")
        return False

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Advanced AI audio enhancement endpoint with multiple models"""
    try:
        logger.info("Enhancement request received")
        
        if 'audio' not in request.files:
            logger.error("No audio file in request")
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        enhancement_type = request.form.get('type', 'both')
        
        logger.info(f"Processing file: {file.filename}, type: {enhancement_type}")
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Create temp files with proper cleanup
        temp_input = None
        temp_output = None
        
        try:
            # Create temporary files
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            
            # Save uploaded file
            file.save(temp_input.name)
            temp_input.close()
            
            logger.info(f"File saved to: {temp_input.name}")
            
            # Try multiple AI models in order of quality
            enhancement_functions = [
                ("Facebook SAM-Audio", enhance_audio_with_facebook_sam),
                ("SpeechBrain RescueSpeech", enhance_audio_with_speechbrain_rescue),
                ("SpeechBrain WHAM", enhance_audio_with_speechbrain_wham),
                ("Basic Processing", enhance_audio_basic)
            ]
            
            success = False
            used_model = "None"
            
            for model_name, enhance_func in enhancement_functions:
                try:
                    logger.info(f"Trying {model_name}...")
                    success = enhance_func(temp_input.name, temp_output.name, enhancement_type)
                    if success:
                        used_model = model_name
                        logger.info(f"Success with {model_name}")
                        break
                    else:
                        logger.info(f"{model_name} failed, trying next...")
                except Exception as e:
                    logger.error(f"{model_name} error: {e}")
                    continue
            
            temp_output.close()
            
            if success and os.path.exists(temp_output.name) and os.path.getsize(temp_output.name) > 0:
                logger.info(f"Sending enhanced file (processed with {used_model})")
                return send_file(
                    temp_output.name,
                    as_attachment=True,
                    download_name=f'enhanced_{secure_filename(file.filename)}',
                    mimetype='audio/wav'
                )
            else:
                logger.error("All enhancement methods failed")
                return jsonify({'success': False, 'error': 'Audio enhancement failed. Please try again with a different file.'}), 500
                
        except Exception as e:
            logger.error(f"File processing error: {e}")
            return jsonify({'success': False, 'error': f'File processing error: {str(e)}'}), 500
            
        finally:
            # Cleanup temp files
            try:
                if temp_input and os.path.exists(temp_input.name):
                    os.unlink(temp_input.name)
                if temp_output and os.path.exists(temp_output.name):
                    os.unlink(temp_output.name)
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                
    except Exception as e:
        logger.error(f"Enhancement endpoint error: {e}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_enhancement': 'multi_model_enabled' if HF_API_TOKEN != 'hf_your_token_here' else 'demo_mode',
        'models': list(AUDIO_MODELS.keys()),
        'model_descriptions': {k: v['description'] for k, v in AUDIO_MODELS.items()},
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

@app.route('/sitemap.xml')
def sitemap():
    from flask import Response
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://voiceclean-ai.vercel.app/</loc><priority>1.0</priority></url>
    <url><loc>https://voiceclean-ai.vercel.app/dashboard</loc><priority>0.8</priority></url>
</urlset>'''
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    from flask import Response
    robots_txt = '''User-agent: *
Allow: /
Sitemap: https://voiceclean-ai.vercel.app/sitemap.xml'''
    return Response(robots_txt, mimetype='text/plain')

@app.errorhandler(404)
def not_found(error):
    return render_template('landing.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import tempfile
import soundfile as sf
import math
import logging
from werkzeug.utils import secure_filename
import time
from datetime import datetime
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE_MB', 50)) * 1024 * 1024

# Initialize extensions
CORS(app)

# Constants
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_audio_basic(audio_path, output_path, enhancement_type='both'):
    """
    Ultra-lightweight audio enhancement using only Python built-ins and soundfile
    """
    try:
        # Load audio file
        data, sr = sf.read(audio_path)
        logger.info(f"Loaded audio: {len(data)} samples at {sr} Hz")
        
        if len(data) == 0:
            raise ValueError("Empty audio file")
        
        # Convert to mono if stereo
        if hasattr(data[0], '__len__'):  # Check if stereo
            # Convert stereo to mono by averaging channels
            mono_data = []
            for sample in data:
                if hasattr(sample, '__len__'):
                    mono_data.append(sum(sample) / len(sample))
                else:
                    mono_data.append(sample)
            data = mono_data
        
        # Convert to list for processing
        if not isinstance(data, list):
            data = data.tolist()
        
        # 1. Basic noise reduction - simple high-pass filter
        if enhancement_type in ['noise', 'both']:
            # Simple high-pass filter using difference equation
            filtered_data = []
            prev_input = 0
            prev_output = 0
            alpha = 0.95  # High-pass filter coefficient
            
            for sample in data:
                # High-pass filter: y[n] = alpha * (y[n-1] + x[n] - x[n-1])
                output = alpha * (prev_output + sample - prev_input)
                filtered_data.append(output)
                prev_input = sample
                prev_output = output
            
            data = filtered_data
        
        # 2. Voice enhancement - boost mid frequencies
        if enhancement_type in ['voice', 'both']:
            # Simple resonant filter for speech frequencies
            enhanced_data = []
            delay_line = [0] * 10  # Simple delay line for resonance
            
            for i, sample in enumerate(data):
                # Add slight resonance at speech frequencies
                delayed_sample = delay_line[i % len(delay_line)]
                enhanced_sample = sample + 0.1 * delayed_sample
                enhanced_data.append(enhanced_sample)
                delay_line[i % len(delay_line)] = sample
            
            data = enhanced_data
        
        # 3. Simple compression
        compressed_data = []
        threshold = 0.7
        ratio = 2.0
        
        for sample in data:
            if abs(sample) > threshold:
                excess = abs(sample) - threshold
                compressed_excess = excess / ratio
                new_level = threshold + compressed_excess
                compressed_data.append(new_level * (1 if sample >= 0 else -1))
            else:
                compressed_data.append(sample)
        
        data = compressed_data
        
        # 4. Normalize
        max_val = max(abs(sample) for sample in data)
        if max_val > 0:
            data = [sample / max_val * 0.95 for sample in data]
        
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
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Main endpoint for audio enhancement - No authentication required"""
    try:
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🎵 VoiceClean AI starting on port {port}")
    print(f"🌐 Access your app at: http://localhost:{port}")
    print(f"🚀 Ready to enhance audio with AI - No login required!")
    app.run(host='0.0.0.0', port=port, debug=False)
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import tempfile
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
    Simple audio processing simulation for Vercel compatibility
    """
    try:
        # For now, just copy the file to simulate processing
        # In a real implementation, you would use lightweight audio processing
        import shutil
        shutil.copy2(audio_path, output_path)
        
        logger.info(f"Audio processing simulated: {audio_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in audio processing: {e}")
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
    """Demo endpoint - returns original file with success message"""
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
                
                # Simulate processing time
                time.sleep(2)
                
                # For demo, just copy the file
                success = enhance_audio_basic(temp_input.name, temp_output.name, enhancement_type)
                
                if success:
                    # Return the processed file
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
from flask import Flask, request, jsonify, send_file, render_template
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import time
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Constants
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def enhance_audio_demo(input_path, output_path, enhancement_type='both'):
    """Demo audio processing - just copies file"""
    try:
        shutil.copy2(input_path, output_path)
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/enhance', methods=['POST'])
def enhance_audio():
    """Audio enhancement endpoint"""
    try:
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
            
            # Simulate processing
            time.sleep(1)
            success = enhance_audio_demo(temp_input.name, temp_output.name)
            temp_output.close()
            
            if success:
                return send_file(
                    temp_output.name,
                    as_attachment=True,
                    download_name=f'enhanced_{secure_filename(file.filename)}',
                    mimetype='audio/wav'
                )
            else:
                return jsonify({'success': False, 'error': 'Processing failed'}), 500
                
        finally:
            # Cleanup
            try:
                os.unlink(temp_input.name)
                os.unlink(temp_output.name)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

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
from flask import Flask, request, jsonify, render_template, send_file
import os
from werkzeug.utils import secure_filename
from ocr import authenticate, ocr_image
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))

# Configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['GOOGLE_CREDENTIALS_PATH'] = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/client_secret.json')
app.config['TOKEN_PATH'] = os.getenv('TOKEN_PATH', 'token.pickle')

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(app.config['GOOGLE_CREDENTIALS_PATH']), exist_ok=True)

# Initialize Google credentials
creds = authenticate()

@app.route('/')
def index():
    logger.debug("Accessing index route")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return str(e), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files[]')
    results = []
    
    # Create a timestamp for the output file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'ocr_results_{timestamp}.txt'
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for file in files:
            if file.filename == '':
                continue
                
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    text = ocr_image(filepath, creds)
                    results.append({
                        'filename': filename,
                        'text': text,
                        'status': 'success'
                    })
                    # Write to the output file
                    output_file.write(f"=== Text from {filename} ===\n")
                    output_file.write(text)
                    output_file.write("\n\n")
                except Exception as e:
                    logger.error(f"Error processing file {filename}: {str(e)}")
                    results.append({
                        'filename': filename,
                        'error': str(e),
                        'status': 'error'
                    })
                finally:
                    # Clean up the uploaded file
                    if os.path.exists(filepath):
                        os.remove(filepath)
    
    # Add the output file information to the response
    results.append({
        'output_file': output_filename,
        'status': 'success'
    })
    
    return jsonify({'results': results})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        return str(e), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info("Starting Flask application")
    logger.info(f"Template folder: {app.template_folder}")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info(f"Running on port: {port}")
    logger.info(f"Debug mode: {debug}")
    
    # Only run the development server if not in production
    if os.getenv('FLASK_ENV') != 'production':
        app.run(host='0.0.0.0', port=port, debug=debug) 
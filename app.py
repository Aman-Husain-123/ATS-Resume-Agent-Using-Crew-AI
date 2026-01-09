"""
Flask Application for ATS Resume Optimization
Beautiful, modern UI with AJAX for smooth user experience
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
from io import BytesIO
from dotenv import load_dotenv

from file_tools.file_loader import detect_and_extract
from crew import run_pipeline
from utils import txt_to_docx_bytes
from pdf_generator import generate_pdf_resume

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_resume():
    """Process resume with AI agents"""
    try:
        # Validate inputs
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        job_title = request.form.get('job_title', '').strip()
        job_description = request.form.get('job_description', '').strip()
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not job_title or not job_description:
            return jsonify({'error': 'Job title and description are required'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use PDF, DOCX, or TXT'}), 400
        
        # Read file
        filename = secure_filename(file.filename)
        file_bytes = file.read()
        
        # Extract text from file
        ext, raw_text = detect_and_extract(filename, file_bytes)
        
        if not raw_text.strip():
            return jsonify({'error': 'Could not extract text from file'}), 400
        
        # Run AI pipeline
        cleaned, rewritten, final_resume, evaluation = run_pipeline(
            raw_resume_text=raw_text,
            job_title=job_title,
            job_description=job_description
        )
        
        # Parse evaluation if possible
        parsed_eval = None
        try:
            eval_text = evaluation.strip().replace("'", '"')
            parsed_eval = json.loads(eval_text)
        except:
            parsed_eval = {'raw': evaluation}
        
        # Return results
        return jsonify({
            'success': True,
            'cleaned': cleaned,
            'rewritten': rewritten,
            'final': final_resume,
            'evaluation': parsed_eval
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<format>/<type>')
def download_resume(format, type):
    """Download resume in specified format"""
    try:
        # Get resume text from session or request
        resume_text = request.args.get('text', '')
        
        if not resume_text:
            return jsonify({'error': 'No resume text provided'}), 400
        
        if format == 'txt':
            # Create text file
            buffer = BytesIO()
            buffer.write(resume_text.encode('utf-8'))
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f'{type}_resume.txt',
                mimetype='text/plain'
            )
        
        elif format == 'docx':
            # Create DOCX file
            docx_bytes = txt_to_docx_bytes(resume_text)
            buffer = BytesIO(docx_bytes)
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f'{type}_resume.docx',
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        
        elif format == 'pdf':
            # Create PDF file
            pdf_bytes = generate_pdf_resume(resume_text)
            buffer = BytesIO(pdf_bytes)
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f'{type}_resume.pdf',
                mimetype='application/pdf'
            )
        
        else:
            return jsonify({'error': 'Invalid format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

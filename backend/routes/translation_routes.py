"""
Translation API Routes
Handles Urdu to English translation requests
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime

from document.upload_handler import UploadHandler
from ocr.ocr_pipeline import OCRPipeline
from translation.setu_translator import SetuTranslator
from document.pdf_generator import PDFGenerator
from common.response_formatter import ResponseFormatter

translation_bp = Blueprint('translation', __name__)

# Initialize components
upload_handler = UploadHandler()
ocr_pipeline = OCRPipeline()
translator = SetuTranslator()
pdf_generator = PDFGenerator()
response_formatter = ResponseFormatter()


@translation_bp.route('/translate-document', methods=['POST'])
def translate_document():
    """
    Translate uploaded document from Urdu to English
    
    Request:
        - file: Image/PDF file
        - options: Translation options (JSON)
    
    Response:
        - original_text: Original Urdu text
        - translated_text: English translation
        - metadata: Translation details
    """
    try:
        start_time = time.time()
        
        # Check if file is present
        if 'file' not in request.files:
            return response_formatter.error_response('No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return response_formatter.error_response('No file selected', 400)
        
        # Get options
        options = request.form.get('options', '{}')
        if isinstance(options, str):
            import json
            options = json.loads(options)
        
        # Upload file
        upload_result = upload_handler.save_file(file)
        if not upload_result['success']:
            return response_formatter.error_response(upload_result['error'], 400)
        
        filepath = upload_result['filepath']
        
        # Run OCR pipeline
        ocr_options = {
            'preprocess': options.get('preprocess', True),
            'clean_text': options.get('clean_text', True),
            'detect_language': True,
            'transliterate': False  # We'll handle translation separately
        }
        
        ocr_result = ocr_pipeline.process(filepath, ocr_options)
        
        if 'error' in ocr_result:
            return response_formatter.error_response(ocr_result['error'], 500)
        
        # Translate the document
        translation_result = translator.translate_document(ocr_result['result'])
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Build response
        response_data = {
            'original': translation_result['original'],
            'translated': translation_result['translated'],
            'metadata': {
                **translation_result['metadata'],
                'total_processing_time': round(processing_time, 2),
                'ocr_confidence': ocr_result['result'].get('metadata', {}).get('ocr_confidence', 0),
                'language_detected': ocr_result['result'].get('language', {}).get('detected', 'unknown')
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return response_formatter.success_response(response_data)
        
    except Exception as e:
        return response_formatter.error_response(f"Translation failed: {str(e)}", 500)


@translation_bp.route('/translate-text', methods=['POST'])
def translate_text():
    """
    Translate plain text from Urdu to English
    
    Request:
        - text: Text to translate
        - source_lang: Source language (default: ur)
        - target_lang: Target language (default: en)
    
    Response:
        - translated_text: Translated text
        - metadata: Translation details
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return response_formatter.error_response('No text provided', 400)
        
        text = data['text']
        source_lang = data.get('source_lang', 'ur')
        target_lang = data.get('target_lang', 'en')
        
        # Translate
        result = translator.translate_text(text, source_lang, target_lang)
        
        response_data = {
            'original_text': text,
            'translated_text': result['translated_text'],
            'metadata': {
                'source_language': result['source_language'],
                'target_language': result['target_language'],
                'confidence': result['confidence'],
                'method': result['method']
            }
        }
        
        return response_formatter.success_response(response_data)
        
    except Exception as e:
        return response_formatter.error_response(f"Translation failed: {str(e)}", 500)


@translation_bp.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from translation data
    
    Request:
        - translation_data: Translation result (JSON)
    
    Response:
        - PDF file download
    """
    try:
        data = request.get_json()
        
        if not data:
            return response_formatter.error_response('No translation data provided', 400)
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_translation_pdf(data)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'translation_{timestamp}.pdf'
        
        # Send file
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return response_formatter.error_response(f"PDF generation failed: {str(e)}", 500)


@translation_bp.route('/translate-and-download', methods=['POST'])
def translate_and_download():
    """
    Translate document and generate PDF in one request
    
    Request:
        - file: Image/PDF file
        - options: Translation options (JSON)
    
    Response:
        - PDF file download
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return response_formatter.error_response('No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return response_formatter.error_response('No file selected', 400)
        
        # Get options
        options = request.form.get('options', '{}')
        if isinstance(options, str):
            import json
            options = json.loads(options)
        
        # Upload file
        upload_result = upload_handler.save_file(file)
        if not upload_result['success']:
            return response_formatter.error_response(upload_result['error'], 400)
        
        filepath = upload_result['filepath']
        
        # Run OCR
        ocr_options = {
            'preprocess': options.get('preprocess', True),
            'clean_text': options.get('clean_text', True),
            'detect_language': True,
            'transliterate': False
        }
        
        ocr_result = ocr_pipeline.process(filepath, ocr_options)
        
        if 'error' in ocr_result:
            return response_formatter.error_response(ocr_result['error'], 500)
        
        # Translate
        translation_result = translator.translate_document(ocr_result['result'])
        
        # Add OCR metadata
        translation_result['metadata']['ocr_confidence'] = \
            ocr_result['result'].get('metadata', {}).get('ocr_confidence', 0)
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_translation_pdf(translation_result)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'jamabandi_translation_{timestamp}.pdf'
        
        # Send file
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return response_formatter.error_response(f"Translation and PDF generation failed: {str(e)}", 500)


@translation_bp.route('/translation-status', methods=['GET'])
def translation_status():
    """Get translation service status"""
    try:
        status = {
            'service': 'Translation API',
            'status': 'operational',
            'setu_available': translator.setu_available,
            'supported_languages': translator.supported_languages,
            'pdf_generation': 'enabled',
            'timestamp': datetime.now().isoformat()
        }
        
        return response_formatter.success_response(status)
        
    except Exception as e:
        return response_formatter.error_response(f"Status check failed: {str(e)}", 500)

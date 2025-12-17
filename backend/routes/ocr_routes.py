"""
OCR API routes
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from document.upload_handler import UploadHandler, PDFHandler
from ocr.ocr_pipeline import OCRPipeline
from common.response_formatter import ResponseFormatter, create_status_response, create_validation_error
from config import Config

logger = logging.getLogger(__name__)

# Create blueprint
ocr_bp = Blueprint('ocr', __name__)

# Initialize components
upload_handler = UploadHandler()
pdf_handler = PDFHandler()
ocr_pipeline = OCRPipeline()

@ocr_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload an image or PDF file for OCR processing
    
    Request:
        - file: Image or PDF file (multipart/form-data)
    
    Returns:
        - filename: Saved filename
        - filepath: Server file path
        - file_info: File metadata
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify(create_validation_error('file', 'No file provided')), 400
        
        file = request.files['file']
        
        # Save file
        save_result = upload_handler.save_file(file)
        
        if not save_result['success']:
            return jsonify(ResponseFormatter.error_response(
                save_result['error'], 400
            ))
        
        # Get file info
        file_info = upload_handler.get_file_info(save_result['filepath'])
        
        return jsonify(ResponseFormatter.success_response(
            data={
                'filename': save_result['filename'],
                'filepath': save_result['filepath'],
                'file_info': file_info
            },
            message='File uploaded successfully'
        ))
    
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))

@ocr_bp.route('/process', methods=['POST'])
def process_ocr():
    """
    Process uploaded image through complete OCR pipeline
    
    Request (JSON):
        - filepath: Path to uploaded file (required)
        - options: Processing options (optional)
            - preprocess: bool (default: true)
            - use_hybrid_ocr: bool (default: false)
            - clean_text: bool (default: true)
            - transliterate: bool (default: true)
            - detect_language: bool (default: true)
    
    Returns:
        - result: Complete OCR processing result
    """
    try:
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify(create_validation_error('filepath', 'Filepath is required')), 400
        
        filepath = data['filepath']
        
        # Check if file exists
        if not os.path.exists(filepath):
            return jsonify(create_validation_error('filepath', 'File not found')), 404
        
        # Get processing options
        options = data.get('options', {})
        
        # Handle PDF files
        if filepath.lower().endswith('.pdf'):
            if not pdf_handler.available:
                return jsonify(ResponseFormatter.error_response(
                    'PDF processing not available. Please install pdf2image.', 500
                ))
            
            # Convert PDF to images
            image_paths = pdf_handler.pdf_to_images(filepath)
            
            # Process first page for now (can be extended to batch)
            filepath = image_paths[0]
        
        # Process through OCR pipeline
        result = ocr_pipeline.process(filepath, options)
        
        return jsonify(ResponseFormatter.success_response(
            data=result,
            message='OCR processing completed'
        ))
    
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))

@ocr_bp.route('/process-upload', methods=['POST'])
def process_upload():
    """
    Combined endpoint: Upload and process in one request
    
    Request:
        - file: Image or PDF file (multipart/form-data)
        - options: JSON string of processing options (optional)
    
    Returns:
        - result: Complete OCR processing result
        - file_info: Uploaded file information
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify(create_validation_error('file', 'No file provided')), 400
        
        file = request.files['file']
        
        # Save file
        save_result = upload_handler.save_file(file)
        
        if not save_result['success']:
            return jsonify(ResponseFormatter.error_response(
                save_result['error'], 400
            ))
        
        filepath = save_result['filepath']
        
        # Get processing options
        import json
        options_str = request.form.get('options', '{}')
        
        try:
            options = json.loads(options_str)
        except:
            options = {}
        
        # Handle PDF files
        if filepath.lower().endswith('.pdf'):
            if not pdf_handler.available:
                return jsonify(ResponseFormatter.error_response(
                    'PDF processing not available', 500
                ))
            
            image_paths = pdf_handler.pdf_to_images(filepath)
            filepath = image_paths[0]
        
        # Process through OCR pipeline
        result = ocr_pipeline.process(filepath, options)
        
        # Add file info to result
        result['file_info'] = {
            'original_filename': file.filename,
            'saved_filename': save_result['filename'],
            'size': save_result['size'],
            'extension': save_result['extension']
        }
        
        return jsonify(ResponseFormatter.success_response(
            data=result,
            message='File uploaded and processed successfully'
        ))
    
    except Exception as e:
        logger.error(f"Upload and process failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))

@ocr_bp.route('/batch', methods=['POST'])
def batch_process():
    """
    Process multiple images in batch
    
    Request:
        - files: Multiple image files (multipart/form-data)
        - options: JSON string of processing options (optional)
    
    Returns:
        - results: List of processing results
        - summary: Batch processing summary
    """
    try:
        if 'files' not in request.files:
            return jsonify(create_validation_error('files', 'No files provided')), 400
        
        files = request.files.getlist('files')
        
        if len(files) > Config.BATCH_SIZE:
            return jsonify(create_validation_error(
                'files',
                f'Too many files. Maximum: {Config.BATCH_SIZE}'
            )), 400
        
        # Save all files
        filepaths = []
        for file in files:
            save_result = upload_handler.save_file(file)
            
            if save_result['success']:
                filepaths.append(save_result['filepath'])
        
        # Get processing options
        import json
        options_str = request.form.get('options', '{}')
        
        try:
            options = json.loads(options_str)
        except:
            options = {}
        
        # Batch process
        batch_result = ocr_pipeline.batch_process(filepaths, options)
        
        return jsonify(ResponseFormatter.success_response(
            data=batch_result,
            message=f'Batch processing completed: {batch_result["successful"]}/{batch_result["total"]} successful'
        ))
    
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))

@ocr_bp.route('/status', methods=['GET'])
def get_status():
    """Get OCR service status"""
    from ocr.ocr_engine import test_ocr_setup
    
    try:
        ocr_status = test_ocr_setup()
        
        return jsonify(ResponseFormatter.success_response(
            data={
                'service': 'OCR API',
                'status': 'running',
                'ocr_setup': ocr_status,
                'batch_size_limit': Config.BATCH_SIZE,
                'max_file_size': Config.MAX_CONTENT_LENGTH,
                'allowed_extensions': list(Config.ALLOWED_EXTENSIONS)
            }
        ))
    
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))

@ocr_bp.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up old uploaded files"""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        deleted_count = upload_handler.cleanup_old_files(max_age_hours)
        
        return jsonify(ResponseFormatter.success_response(
            data={'deleted_files': deleted_count},
            message=f'Cleaned up {deleted_count} old files'
        ))
    
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))

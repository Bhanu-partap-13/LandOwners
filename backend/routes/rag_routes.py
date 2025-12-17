"""
RAG-based Document Processing API Routes
Handles large PDF processing with streaming support
"""
from flask import Blueprint, request, jsonify, Response, stream_with_context
import os
import json
import logging
import time
from werkzeug.utils import secure_filename
from document.rag_document_processor import RAGDocumentProcessor
from common.response_formatter import ResponseFormatter, create_validation_error
from config import Config

logger = logging.getLogger(__name__)

# Create blueprint
rag_bp = Blueprint('rag', __name__)

# Initialize RAG processor (singleton for caching efficiency)
_rag_processor = None

def get_rag_processor():
    """Get or create RAG processor instance"""
    global _rag_processor
    if _rag_processor is None:
        cache_dir = os.path.join(Config.UPLOAD_FOLDER, '..', 'cache', 'rag')
        _rag_processor = RAGDocumentProcessor(cache_dir=cache_dir)
    return _rag_processor


@rag_bp.route('/process', methods=['POST'])
def process_pdf():
    """
    Process a PDF file using RAG approach
    
    Request (JSON):
        - filepath: Path to PDF file (required)
        - translate: Whether to translate (default: true)
        - streaming: Use streaming response (default: false)
        - use_cache: Use cached results (default: true)
    
    Returns:
        - result: Processing result with all pages
    """
    try:
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify(create_validation_error('filepath', 'PDF filepath is required')), 400
        
        filepath = data['filepath']
        
        if not os.path.exists(filepath):
            return jsonify(create_validation_error('filepath', 'File not found')), 404
        
        if not filepath.lower().endswith('.pdf'):
            return jsonify(create_validation_error('filepath', 'File must be a PDF')), 400
        
        # Get options
        translate = data.get('translate', True)
        use_cache = data.get('use_cache', True)
        
        processor = get_rag_processor()
        
        # Process PDF in batch mode
        result = processor.process_pdf_batch(
            filepath,
            translate=translate,
            use_cache=use_cache
        )
        
        return jsonify(ResponseFormatter.success_response(
            data=result,
            message=f'Processed {result["total_pages"]} pages successfully'
        ))
    
    except Exception as e:
        logger.error(f"RAG processing failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))


@rag_bp.route('/process/stream', methods=['POST'])
def process_pdf_stream():
    """
    Process PDF with streaming response (recommended for large PDFs)
    
    Results are streamed page by page as Server-Sent Events (SSE)
    
    Request (JSON):
        - filepath: Path to PDF file (required)
        - translate: Whether to translate (default: true)
        - use_cache: Use cached results (default: true)
    
    Returns:
        - Stream of JSON objects, one per page
    """
    try:
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify(create_validation_error('filepath', 'PDF filepath is required')), 400
        
        filepath = data['filepath']
        
        if not os.path.exists(filepath):
            return jsonify(create_validation_error('filepath', 'File not found')), 404
        
        if not filepath.lower().endswith('.pdf'):
            return jsonify(create_validation_error('filepath', 'File must be a PDF')), 400
        
        translate = data.get('translate', True)
        use_cache = data.get('use_cache', True)
        
        processor = get_rag_processor()
        
        def generate():
            """Generator for streaming response"""
            try:
                for page_result in processor.process_pdf_streaming(
                    filepath,
                    translate=translate,
                    use_cache=use_cache
                ):
                    # Send as Server-Sent Event
                    yield f"data: {json.dumps(page_result, ensure_ascii=False)}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'event': 'complete', 'progress': processor.get_progress()})}\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: {json.dumps({'event': 'error', 'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    except Exception as e:
        logger.error(f"Stream setup failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))


@rag_bp.route('/progress', methods=['GET'])
def get_progress():
    """
    Get current processing progress
    
    Returns:
        - progress: Processing progress information
    """
    processor = get_rag_processor()
    progress = processor.get_progress()
    
    return jsonify(ResponseFormatter.success_response(
        data=progress,
        message='Progress retrieved'
    ))


@rag_bp.route('/search', methods=['POST'])
def search_document():
    """
    Search processed document using semantic similarity
    
    Request (JSON):
        - query: Search query text (required)
        - top_k: Number of results (default: 5)
    
    Returns:
        - results: Matching chunks with similarity scores
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify(create_validation_error('query', 'Search query is required')), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        processor = get_rag_processor()
        results = processor.search_document(query, top_k)
        
        return jsonify(ResponseFormatter.success_response(
            data={'results': results, 'count': len(results)},
            message=f'Found {len(results)} matching chunks'
        ))
    
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))


@rag_bp.route('/translate/query', methods=['POST'])
def translate_query():
    """
    RAG-style translation: find relevant chunks and return translations
    
    Request (JSON):
        - query: Query text in source language (required)
        - context_chunks: Number of context chunks (default: 3)
    
    Returns:
        - translations: Relevant translations with context
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify(create_validation_error('query', 'Query is required')), 400
        
        query = data['query']
        context_chunks = data.get('context_chunks', 3)
        
        processor = get_rag_processor()
        result = processor.get_translation_for_query(query, context_chunks)
        
        return jsonify(ResponseFormatter.success_response(
            data=result,
            message='Translation context retrieved'
        ))
    
    except Exception as e:
        logger.error(f"Query translation failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))


@rag_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear RAG cache
    
    Request (JSON):
        - doc_hash: Specific document hash to clear (optional)
                   If not provided, clears all cache
    
    Returns:
        - message: Success message
    """
    try:
        data = request.get_json() or {}
        doc_hash = data.get('doc_hash')
        
        processor = get_rag_processor()
        processor.clear_cache(doc_hash)
        
        return jsonify(ResponseFormatter.success_response(
            message='Cache cleared successfully'
        ))
    
    except Exception as e:
        logger.error(f"Cache clear failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))


@rag_bp.route('/upload-and-process', methods=['POST'])
def upload_and_process():
    """
    Upload a PDF and immediately start RAG processing
    
    Request:
        - file: PDF file (multipart/form-data)
        - translate: Whether to translate (form field, default: true)
    
    Returns:
        - Processing result
    """
    try:
        if 'file' not in request.files:
            return jsonify(create_validation_error('file', 'No file provided')), 400
        
        file = request.files['file']
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify(create_validation_error('file', 'File must be a PDF')), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get options
        translate = request.form.get('translate', 'true').lower() == 'true'
        
        processor = get_rag_processor()
        
        # Process PDF
        result = processor.process_pdf_batch(
            filepath,
            translate=translate,
            use_cache=True
        )
        
        return jsonify(ResponseFormatter.success_response(
            data={
                'filename': filename,
                'filepath': filepath,
                'processing_result': result
            },
            message=f'Uploaded and processed {result["total_pages"]} pages'
        ))
    
    except Exception as e:
        logger.error(f"Upload and process failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))


@rag_bp.route('/estimate', methods=['POST'])
def estimate_processing_time():
    """
    Estimate processing time for a PDF
    
    Request (JSON):
        - filepath: Path to PDF file (required)
        - translate: Whether translation is needed (default: true)
    
    Returns:
        - estimate: Processing time estimate
    """
    try:
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify(create_validation_error('filepath', 'PDF filepath is required')), 400
        
        filepath = data['filepath']
        
        if not os.path.exists(filepath):
            return jsonify(create_validation_error('filepath', 'File not found')), 404
        
        # Get page count
        import fitz
        doc = fitz.open(filepath)
        page_count = len(doc)
        doc.close()
        
        # Estimate times (based on typical processing rates)
        ocr_time_per_page = 2.0  # seconds
        translation_time_per_page = 1.5  # seconds
        
        translate = data.get('translate', True)
        
        total_time = page_count * ocr_time_per_page
        if translate:
            total_time += page_count * translation_time_per_page
        
        return jsonify(ResponseFormatter.success_response(
            data={
                'page_count': page_count,
                'estimated_time_seconds': round(total_time, 1),
                'estimated_time_formatted': format_time(total_time),
                'includes_translation': translate
            },
            message=f'Estimated time for {page_count} pages'
        ))
    
    except Exception as e:
        logger.error(f"Estimation failed: {str(e)}")
        return jsonify(ResponseFormatter.error_response(str(e), 500))


def format_time(seconds: float) -> str:
    """Format seconds to human readable string"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes} min {secs} sec"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours} hr {minutes} min"

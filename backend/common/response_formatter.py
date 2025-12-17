"""
Response formatter for API responses
Structures OCR results in consistent format
"""
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Format API responses consistently"""
    
    @staticmethod
    def success_response(data, message=None, metadata=None):
        """
        Format successful response
        
        Args:
            data: Response data
            message: Optional message
            metadata: Optional metadata
        
        Returns:
            dict: Formatted response
        """
        response = {
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if message:
            response['message'] = message
        
        if metadata:
            response['metadata'] = metadata
        
        return response
    
    @staticmethod
    def error_response(error, status_code=500, details=None):
        """
        Format error response
        
        Args:
            error: Error message
            status_code: HTTP status code
            details: Optional error details
        
        Returns:
            tuple: (response dict, status code)
        """
        response = {
            'success': False,
            'error': str(error),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            response['details'] = details
        
        return response, status_code
    
    @staticmethod
    def format_ocr_result(
        raw_text,
        cleaned_text=None,
        transliterated_text=None,
        language_detected=None,
        confidence_score=None,
        processing_time=None,
        preprocessing_info=None,
        metadata=None
    ):
        """
        Format OCR processing result
        
        Args:
            raw_text: Raw OCR output
            cleaned_text: Cleaned text
            transliterated_text: Transliterated text
            language_detected: Detected language info
            confidence_score: OCR confidence
            processing_time: Time taken
            preprocessing_info: Image preprocessing details
            metadata: Additional metadata
        
        Returns:
            dict: Formatted OCR result
        """
        result = {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text or raw_text,
            'transliterated_text': transliterated_text,
            'language': language_detected,
            'confidence': {
                'ocr_confidence': confidence_score,
                'quality_score': None  # Can be calculated
            },
            'processing': {
                'time_seconds': processing_time,
                'preprocessing_steps': preprocessing_info or [],
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        if metadata:
            result['metadata'] = metadata
        
        return result
    
    @staticmethod
    def format_batch_result(results, total_time=None):
        """
        Format batch processing result
        
        Args:
            results: List of individual results
            total_time: Total processing time
        
        Returns:
            dict: Formatted batch result
        """
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        return {
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'results': results,
            'processing': {
                'total_time_seconds': total_time,
                'average_time_seconds': total_time / len(results) if results and total_time else None,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

class OCRResultBuilder:
    """Build comprehensive OCR result with all components"""
    
    def __init__(self):
        self.start_time = time.time()
        self.stages = {}
        self.errors = []
    
    def add_stage(self, stage_name, duration, success=True, data=None):
        """Add a processing stage"""
        self.stages[stage_name] = {
            'duration': duration,
            'success': success,
            'data': data
        }
    
    def add_error(self, stage, error):
        """Add an error"""
        self.errors.append({
            'stage': stage,
            'error': str(error),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def build(
        self,
        raw_text,
        cleaned_text=None,
        transliterated_text=None,
        language_info=None,
        ocr_confidence=None,
        preprocessing_info=None
    ):
        """Build final result"""
        total_time = time.time() - self.start_time
        
        return {
            'success': len(self.errors) == 0,
            'result': {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'transliterated_text': transliterated_text,
                'language': language_info,
                'confidence': ocr_confidence
            },
            'processing': {
                'total_time': round(total_time, 3),
                'stages': self.stages,
                'preprocessing': preprocessing_info
            },
            'errors': self.errors if self.errors else None,
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            }
        }

def create_status_response(status, progress=None, message=None):
    """Create processing status response"""
    response = {
        'status': status,  # 'pending', 'processing', 'completed', 'failed'
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if progress is not None:
        response['progress'] = {
            'percentage': progress,
            'message': message
        }
    
    if message:
        response['message'] = message
    
    return response

def create_validation_error(field, message):
    """Create validation error response"""
    return {
        'success': False,
        'error': 'Validation error',
        'details': {
            'field': field,
            'message': message
        },
        'timestamp': datetime.utcnow().isoformat()
    }

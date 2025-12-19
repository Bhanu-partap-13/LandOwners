"""
Lightweight OCR Engine - Cloud API Based
Replaces heavy Tesseract + PyTorch with cloud APIs:
1. Bhashini (Gov of India) - FREE
2. Google Cloud Vision - 1000 FREE/month
3. Simple local fallback using PIL

No heavy dependencies required!
"""

import os
import io
import logging
from typing import Dict, List, Optional, Union
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class LightweightOCR:
    """
    Lightweight OCR engine using cloud APIs
    No Tesseract or PyTorch required!
    """
    
    def __init__(self, preferred_backend: str = 'auto'):
        """
        Initialize lightweight OCR
        
        Args:
            preferred_backend: 'bhashini', 'google', or 'auto' (try best available)
        """
        self.preferred_backend = preferred_backend
        self._unified_service = None
        self._bhashini = None
        self._google = None
        
        # Lazy load services
        self._initialized = False
        logger.info(f"LightweightOCR initialized (backend preference: {preferred_backend})")
    
    def _init_services(self):
        """Lazy initialization of cloud services"""
        if self._initialized:
            return
        
        try:
            from services.bhashini_service import BhashiniService, GoogleVisionOCR, UnifiedOCRService
            self._unified_service = UnifiedOCRService()
            self._bhashini = self._unified_service.bhashini
            self._google = self._unified_service.google_vision
        except ImportError as e:
            logger.warning(f"Could not import services: {e}")
        
        self._initialized = True
    
    def is_available(self) -> bool:
        """Check if any OCR backend is available"""
        self._init_services()
        return self._unified_service and self._unified_service.is_available()
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backends"""
        self._init_services()
        if self._unified_service:
            return self._unified_service.backends
        return []
    
    def _prepare_image(self, image_input: Union[str, bytes, Image.Image, np.ndarray]) -> bytes:
        """
        Convert any image input to bytes
        
        Args:
            image_input: File path, bytes, PIL Image, or numpy array
        
        Returns:
            Image as JPEG bytes
        """
        if isinstance(image_input, bytes):
            return image_input
        
        if isinstance(image_input, str):
            # File path
            if os.path.exists(image_input):
                with open(image_input, 'rb') as f:
                    return f.read()
            else:
                raise FileNotFoundError(f"Image file not found: {image_input}")
        
        if isinstance(image_input, np.ndarray):
            # Convert numpy to PIL
            image = Image.fromarray(image_input)
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save to bytes
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        return buffer.getvalue()
    
    def extract_text(self, image_input, source_lang: str = 'ur', 
                     config_params: str = None) -> Dict:
        """
        Extract text from image using cloud OCR API
        
        Args:
            image_input: Image file path, bytes, PIL Image, or numpy array
            source_lang: Expected language ('ur', 'hi', 'en')
            config_params: Ignored (for compatibility with old API)
        
        Returns:
            dict: {
                'text': extracted text,
                'confidence': confidence score,
                'details': additional info,
                'word_count': approximate word count,
                'source': which backend was used
            }
        """
        self._init_services()
        
        if not self.is_available():
            raise RuntimeError(
                "No OCR backend available. Please configure:\n"
                "1. Bhashini API: Set BHASHINI_USER_ID and BHASHINI_API_KEY\n"
                "   Register free at: https://bhashini.gov.in/ulca/user/register\n"
                "2. Google Vision: Set GOOGLE_CLOUD_API_KEY\n"
                "   Get API key at: https://console.cloud.google.com"
            )
        
        try:
            # Prepare image
            image_bytes = self._prepare_image(image_input)
            
            # Use unified service
            result = self._unified_service.ocr(image_bytes, source_lang)
            
            text = result.get('text', '')
            
            return {
                'text': text.strip(),
                'confidence': result.get('confidence', 85.0),
                'details': {'backend': result.get('source', 'unknown')},
                'word_count': len(text.split()) if text else 0,
                'source': result.get('source', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise
    
    def extract_and_translate(self, image_input, source_lang: str = 'ur',
                               target_lang: str = 'en') -> Dict:
        """
        Extract text and translate in one call (more efficient)
        
        Args:
            image_input: Image input
            source_lang: Source language
            target_lang: Target language
        
        Returns:
            dict with extracted_text and translated_text
        """
        self._init_services()
        
        if not self.is_available():
            raise RuntimeError("No OCR backend available")
        
        try:
            image_bytes = self._prepare_image(image_input)
            result = self._unified_service.ocr_and_translate(
                image_bytes, source_lang, target_lang
            )
            return result
        except Exception as e:
            logger.error(f"OCR+Translation failed: {e}")
            raise
    
    def extract_with_boxes(self, image_input) -> List[Dict]:
        """
        Extract text with bounding boxes
        Note: Simplified implementation - returns whole text as single box
        
        For detailed boxes, use Google Vision directly
        """
        result = self.extract_text(image_input)
        
        # Return simplified single box result
        return [{
            'text': result.get('text', ''),
            'confidence': result.get('confidence', 0),
            'box': {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        }]
    
    def extract_by_language(self, image_input) -> Dict[str, str]:
        """
        Try to extract text for different languages
        """
        results = {}
        
        for lang in ['en', 'hi', 'ur']:
            try:
                result = self.extract_text(image_input, source_lang=lang)
                results[lang] = result.get('text', '')
            except Exception as e:
                logger.warning(f"Failed to extract for {lang}: {e}")
                results[lang] = ''
        
        return results
    
    def get_available_languages(self) -> List[str]:
        """Get list of supported languages"""
        return ['en', 'hi', 'ur', 'pa', 'ta', 'te', 'bn', 'gu', 'kn', 'ml', 'mr', 'or']


# Compatibility alias for existing code
class MultiLanguageOCR(LightweightOCR):
    """
    Alias for LightweightOCR to maintain compatibility with existing code
    """
    
    def __init__(self, languages: str = 'eng+hin+urd', **kwargs):
        """
        Initialize with language string (for backward compatibility)
        
        Args:
            languages: Language string like 'eng+hin+urd' (ignored, we use cloud)
        """
        super().__init__(**kwargs)
        self.languages = languages
        logger.info(f"MultiLanguageOCR initialized (lightweight mode)")


# Keep TesseractOCR as fallback if pytesseract is installed
class TesseractOCR:
    """
    Legacy Tesseract OCR - only used if explicitly requested
    Requires pytesseract to be installed
    """
    
    def __init__(self, tesseract_path: str = None, languages: str = 'eng+hin+urd'):
        self.languages = languages
        self._available = False
        
        try:
            import pytesseract
            self._pytesseract = pytesseract
            
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
            self._available = True
            logger.info("TesseractOCR initialized (legacy mode)")
        except ImportError:
            logger.info("pytesseract not installed - TesseractOCR not available")
    
    def is_available(self) -> bool:
        return self._available
    
    def extract_text(self, image_input, config_params: str = None) -> Dict:
        """Extract text using Tesseract"""
        if not self._available:
            raise RuntimeError("Tesseract not available")
        
        if isinstance(image_input, str):
            image = Image.open(image_input)
        elif isinstance(image_input, np.ndarray):
            image = Image.fromarray(image_input)
        else:
            image = image_input
        
        config = config_params or '--oem 3 --psm 6'
        
        text = self._pytesseract.image_to_string(
            image, lang=self.languages, config=config
        )
        
        return {
            'text': text.strip(),
            'confidence': 0,  # Tesseract doesn't return confidence easily
            'details': {},
            'word_count': len(text.split()) if text else 0,
            'source': 'tesseract'
        }

"""
Lightweight OCR Pipeline
Uses cloud APIs (Bhashini/Google Vision) instead of local heavy models
"""
import time
import os
import logging
import tempfile
from typing import Dict, Optional, List
from PIL import Image
import numpy as np

# PDF handling
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)


class LightweightOCRPipeline:
    """
    Lightweight OCR pipeline using cloud APIs
    
    Workflow:
    1. PDF to image conversion (PyMuPDF - no external deps)
    2. Image preprocessing (OpenCV - lightweight)
    3. OCR via Bhashini API (FREE) or Google Vision (fallback)
    4. Translation via Bhashini API
    5. Language detection (lightweight)
    """
    
    def __init__(self):
        """Initialize pipeline components"""
        logger.info("Initializing Lightweight OCR Pipeline...")
        
        # Lazy-loaded components
        self._ocr_service = None
        self._translator = None
        self._preprocessor = None
        self._language_detector = None
        
        self.temp_files = []
        
        logger.info(f"Lightweight Pipeline initialized (PyMuPDF: {PYMUPDF_AVAILABLE})")
    
    @property
    def ocr_service(self):
        """Lazy load OCR service"""
        if self._ocr_service is None:
            try:
                from ocr.lightweight_ocr import LightweightOCR
                self._ocr_service = LightweightOCR()
            except ImportError:
                logger.error("Could not import LightweightOCR")
        return self._ocr_service
    
    @property
    def translator(self):
        """Lazy load translator"""
        if self._translator is None:
            try:
                from translation.lightweight_translator import LightweightTranslator
                self._translator = LightweightTranslator()
            except ImportError:
                logger.error("Could not import LightweightTranslator")
        return self._translator
    
    @property
    def preprocessor(self):
        """Lazy load image preprocessor"""
        if self._preprocessor is None:
            try:
                from ocr.image_processing import ImagePreprocessor
                self._preprocessor = ImagePreprocessor()
            except ImportError:
                logger.warning("ImagePreprocessor not available")
        return self._preprocessor
    
    @property
    def language_detector(self):
        """Lazy load language detector"""
        if self._language_detector is None:
            try:
                from translation.language_detector import SmartLanguageDetector
                self._language_detector = SmartLanguageDetector()
            except ImportError:
                logger.warning("SmartLanguageDetector not available")
        return self._language_detector
    
    def _is_pdf(self, file_path: str) -> bool:
        """Check if file is a PDF"""
        return file_path.lower().endswith('.pdf')
    
    def _convert_pdf_to_images(self, pdf_path: str, dpi: int = 200) -> List[str]:
        """
        Convert PDF pages to images using PyMuPDF
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")
        
        image_paths = []
        logger.info(f"Converting PDF to images: {pdf_path}")
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            logger.info(f"PDF has {total_pages} pages")
            
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # Render page to image
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Save to temp file
                temp_path = os.path.join(
                    tempfile.gettempdir(), 
                    f"ocr_page_{page_num}_{time.time()}.png"
                )
                pix.save(temp_path)
                image_paths.append(temp_path)
                self.temp_files.append(temp_path)
            
            doc.close()
            logger.info(f"PDF converted: {len(image_paths)} images")
            return image_paths
            
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
        self.temp_files = []
    
    def _read_image_bytes(self, image_path: str) -> bytes:
        """Read image file as bytes"""
        with open(image_path, 'rb') as f:
            return f.read()
    
    def process(self, image_path: str, options: Dict = None) -> Dict:
        """
        Process image or PDF through OCR pipeline
        
        Args:
            image_path: Path to input image or PDF
            options: Processing options:
                - preprocess: bool (default: True)
                - translate: bool (default: True)
                - source_lang: str (default: 'ur')
                - target_lang: str (default: 'en')
                - detect_language: bool (default: True)
        
        Returns:
            dict: Complete processing result
        """
        options = options or {}
        
        opts = {
            'preprocess': options.get('preprocess', True),
            'translate': options.get('translate', True),
            'source_lang': options.get('source_lang', 'ur'),
            'target_lang': options.get('target_lang', 'en'),
            'detect_language': options.get('detect_language', True),
            'use_hybrid_ocr': options.get('use_hybrid_ocr', False),  # Ignored in lightweight
            'clean_text': options.get('clean_text', True),
            'transliterate': options.get('transliterate', True),
        }
        
        start_time = time.time()
        stages = []
        
        try:
            # Handle PDF files
            if self._is_pdf(image_path):
                logger.info(f"Processing PDF: {image_path}")
                return self._process_pdf(image_path, opts, start_time, stages)
            
            # Process single image
            return self._process_single_image(image_path, opts, start_time, stages)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return self._build_error_result(str(e), time.time() - start_time, stages)
        finally:
            self._cleanup_temp_files()
    
    def _process_single_image(self, image_path: str, opts: Dict, 
                               start_time: float, stages: List) -> Dict:
        """Process a single image"""
        
        raw_text = ""
        translated_text = ""
        ocr_confidence = 0
        detected_lang = opts['source_lang']
        
        try:
            # Stage 1: Preprocessing (optional)
            if opts['preprocess'] and self.preprocessor:
                stage_start = time.time()
                try:
                    preprocessed = self.preprocessor.preprocess(image_path)
                    # Save preprocessed image temporarily
                    if isinstance(preprocessed, np.ndarray):
                        temp_path = os.path.join(tempfile.gettempdir(), f"preprocessed_{time.time()}.png")
                        Image.fromarray(preprocessed).save(temp_path)
                        self.temp_files.append(temp_path)
                        image_path = temp_path
                    stages.append({
                        'name': 'preprocessing',
                        'duration': time.time() - stage_start,
                        'success': True
                    })
                except Exception as e:
                    logger.warning(f"Preprocessing failed: {e}")
                    stages.append({
                        'name': 'preprocessing',
                        'duration': time.time() - stage_start,
                        'success': False,
                        'error': str(e)
                    })
            
            # Stage 2: OCR
            stage_start = time.time()
            
            if self.ocr_service and self.ocr_service.is_available():
                try:
                    # Use combined OCR+Translation if available
                    if opts['translate']:
                        result = self.ocr_service.extract_and_translate(
                            image_path,
                            source_lang=opts['source_lang'],
                            target_lang=opts['target_lang']
                        )
                        raw_text = result.get('extracted_text', '')
                        translated_text = result.get('translated_text', '')
                        ocr_confidence = 85.0
                        
                        stages.append({
                            'name': 'ocr_translate',
                            'duration': time.time() - stage_start,
                            'success': True,
                            'backend': result.get('source', 'unknown')
                        })
                    else:
                        result = self.ocr_service.extract_text(
                            image_path, 
                            source_lang=opts['source_lang']
                        )
                        raw_text = result.get('text', '')
                        ocr_confidence = result.get('confidence', 0)
                        
                        stages.append({
                            'name': 'ocr',
                            'duration': time.time() - stage_start,
                            'success': True,
                            'backend': result.get('source', 'unknown')
                        })
                        
                except Exception as e:
                    logger.error(f"OCR failed: {e}")
                    stages.append({
                        'name': 'ocr',
                        'duration': time.time() - stage_start,
                        'success': False,
                        'error': str(e)
                    })
            else:
                stages.append({
                    'name': 'ocr',
                    'duration': 0,
                    'success': False,
                    'error': 'No OCR service available'
                })
            
            # Stage 3: Language Detection (if enabled)
            if opts['detect_language'] and raw_text:
                stage_start = time.time()
                try:
                    if self.translator:
                        detected_lang = self.translator.detect_language(raw_text)
                    stages.append({
                        'name': 'language_detection',
                        'duration': time.time() - stage_start,
                        'success': True,
                        'detected': detected_lang
                    })
                except Exception as e:
                    logger.warning(f"Language detection failed: {e}")
            
            # Stage 4: Translation (if not already done and enabled)
            if opts['translate'] and raw_text and not translated_text:
                stage_start = time.time()
                if self.translator and self.translator.is_available():
                    try:
                        trans_result = self.translator.translate(
                            raw_text,
                            source_lang=detected_lang or opts['source_lang'],
                            target_lang=opts['target_lang']
                        )
                        translated_text = trans_result.get('translated_text', '')
                        stages.append({
                            'name': 'translation',
                            'duration': time.time() - stage_start,
                            'success': True,
                            'method': trans_result.get('method', 'unknown')
                        })
                    except Exception as e:
                        logger.error(f"Translation failed: {e}")
                        stages.append({
                            'name': 'translation',
                            'duration': time.time() - stage_start,
                            'success': False,
                            'error': str(e)
                        })
            
            # Build result
            total_duration = time.time() - start_time
            
            return {
                'success': True,
                'result': {
                    'raw_text': raw_text,
                    'cleaned_text': raw_text,  # In lightweight mode, minimal cleaning
                    'translated_text': translated_text,
                    'transliterated_text': raw_text,  # Placeholder
                    'language': {
                        'detected': detected_lang,
                        'confidence': 0.9 if detected_lang != 'unknown' else 0
                    },
                    'metadata': {
                        'ocr_confidence': ocr_confidence,
                        'processing_time': total_duration,
                        'stages': stages,
                        'mode': 'lightweight',
                        'backends_used': [s.get('backend') for s in stages if s.get('backend')]
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return self._build_error_result(str(e), time.time() - start_time, stages)
    
    def _process_pdf(self, pdf_path: str, opts: Dict, 
                     start_time: float, stages: List) -> Dict:
        """Process a PDF file"""
        
        try:
            # Convert PDF to images
            stage_start = time.time()
            image_paths = self._convert_pdf_to_images(pdf_path)
            stages.append({
                'name': 'pdf_conversion',
                'duration': time.time() - stage_start,
                'success': True,
                'pages': len(image_paths)
            })
            
            # Process each page
            all_raw_text = []
            all_translated_text = []
            total_confidence = 0
            
            for i, img_path in enumerate(image_paths):
                logger.info(f"Processing page {i + 1}/{len(image_paths)}")
                
                page_result = self._process_single_image(img_path, opts, time.time(), [])
                
                if page_result.get('success'):
                    result_data = page_result.get('result', {})
                    raw = result_data.get('raw_text', '')
                    trans = result_data.get('translated_text', '')
                    
                    if raw.strip():
                        all_raw_text.append(f"--- Page {i + 1} ---\n{raw}")
                    if trans.strip():
                        all_translated_text.append(f"--- Page {i + 1} ---\n{trans}")
                    
                    total_confidence += result_data.get('metadata', {}).get('ocr_confidence', 0)
            
            # Combine results
            combined_raw = '\n\n'.join(all_raw_text)
            combined_translated = '\n\n'.join(all_translated_text)
            avg_confidence = total_confidence / len(image_paths) if image_paths else 0
            
            total_duration = time.time() - start_time
            
            return {
                'success': True,
                'result': {
                    'raw_text': combined_raw,
                    'cleaned_text': combined_raw,
                    'translated_text': combined_translated,
                    'transliterated_text': combined_raw,
                    'language': {'detected': opts['source_lang']},
                    'metadata': {
                        'ocr_confidence': avg_confidence,
                        'processing_time': total_duration,
                        'stages': stages,
                        'mode': 'lightweight',
                        'page_count': len(image_paths)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return self._build_error_result(str(e), time.time() - start_time, stages)
    
    def _build_error_result(self, error: str, duration: float, stages: List) -> Dict:
        """Build error result"""
        return {
            'success': False,
            'error': error,
            'result': {
                'raw_text': '',
                'cleaned_text': '',
                'translated_text': '',
                'transliterated_text': '',
                'language': {'detected': 'unknown'},
                'metadata': {
                    'ocr_confidence': 0,
                    'processing_time': duration,
                    'stages': stages,
                    'mode': 'lightweight'
                }
            }
        }


# Compatibility wrapper for existing code
class OCRPipeline(LightweightOCRPipeline):
    """
    Compatibility alias for existing OCRPipeline usage
    Now uses lightweight cloud-based processing
    """
    pass

"""
Complete OCR Pipeline Orchestrator
Chains all processing steps together
Supports both images and PDF files
"""
import time
import os
import logging
import tempfile
import cv2
import numpy as np
from ocr.image_processing import ImagePreprocessor
from ocr.ocr_engine import MultiLanguageOCR
from ocr.urdu_ocr import HybridOCR
from translation.language_detector import SmartLanguageDetector
from common.text_cleaner import AdvancedTextCleaner
from translation.transliterator import SmartTransliterator
from common.response_formatter import OCRResultBuilder
from config import Config

# PDF handling
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

logger = logging.getLogger(__name__)

class OCRPipeline:
    """
    Complete OCR pipeline that orchestrates all processing steps:
    1. PDF to image conversion (if needed)
    2. Image preprocessing
    3. OCR (Tesseract or Transformer-based)
    4. Language detection
    5. Text cleaning
    6. Transliteration
    """
    
    def __init__(self):
        """Initialize pipeline components"""
        logger.info("Initializing OCR Pipeline...")
        
        self.preprocessor = ImagePreprocessor()
        self.multilang_ocr = MultiLanguageOCR()
        self.hybrid_ocr = HybridOCR()
        self.language_detector = SmartLanguageDetector()
        self.text_cleaner = AdvancedTextCleaner(Config.SETU_PATH)
        self.transliterator = SmartTransliterator(Config.SETU_TRANSLATE_PATH)
        self.temp_files = []  # Track temp files for cleanup
        
        logger.info(f"OCR Pipeline initialized (PyMuPDF available: {PYMUPDF_AVAILABLE})")
    
    def _is_pdf(self, file_path: str) -> bool:
        """Check if file is a PDF"""
        return file_path.lower().endswith('.pdf')
    
    def _convert_pdf_to_images(self, pdf_path: str, dpi: int = 200) -> list:
        """
        Convert PDF pages to images using PyMuPDF
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for rendering (default 200)
            
        Returns:
            List of image paths (temp files)
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
                zoom = dpi / 72  # 72 is default PDF DPI
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
                
                logger.debug(f"Converted page {page_num + 1}/{total_pages}")
            
            doc.close()
            logger.info(f"PDF converted: {len(image_paths)} images created")
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
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        self.temp_files = []

    def process(self, image_path, options=None):
        """
        Process image or PDF through complete OCR pipeline
        
        Args:
            image_path: Path to input image or PDF
            options: Processing options dict:
                - preprocess: bool (default: True)
                - use_hybrid_ocr: bool (default: False) - Use hybrid OCR for handwritten
                - clean_text: bool (default: True)
                - transliterate: bool (default: True)
                - detect_language: bool (default: True)
        
        Returns:
            dict: Complete processing result
        """
        if options is None:
            options = {}
        
        # Default options
        opts = {
            'preprocess': options.get('preprocess', True),
            'use_hybrid_ocr': options.get('use_hybrid_ocr', False),
            'clean_text': options.get('clean_text', True),
            'transliterate': options.get('transliterate', True),
            'detect_language': options.get('detect_language', True)
        }
        
        result_builder = OCRResultBuilder()
        
        try:
            # Handle PDF files - convert to images first
            if self._is_pdf(image_path):
                logger.info(f"Processing PDF file: {image_path}")
                return self._process_pdf(image_path, opts, result_builder)
            
            # Process single image
            return self._process_single_image(image_path, opts, result_builder)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            result_builder.add_error(f"Pipeline failed: {e}")
            return result_builder.build(
                raw_text='',
                cleaned_text='',
                transliterated_text='',
                language_info={'detected': 'unknown'},
                ocr_confidence=0,
                preprocessing_info=None
            )
        finally:
            # Always cleanup temp files
            self._cleanup_temp_files()
    
    def _process_pdf(self, pdf_path: str, opts: dict, result_builder) -> dict:
        """Process a PDF file by converting pages to images and running OCR"""
        try:
            # Convert PDF to images
            stage_start = time.time()
            logger.info("Stage 0: PDF to image conversion")
            
            image_paths = self._convert_pdf_to_images(pdf_path, dpi=200)
            
            stage_duration = time.time() - stage_start
            result_builder.add_stage(
                'pdf_conversion',
                stage_duration,
                success=True,
                data={'pages': len(image_paths)}
            )
            
            # Process each page and combine results
            all_raw_text = []
            all_cleaned_text = []
            total_confidence = 0
            preprocessing_info = None
            language_info = None
            
            for i, img_path in enumerate(image_paths):
                logger.info(f"Processing page {i + 1}/{len(image_paths)}")
                
                # Process this page
                page_result = self._process_single_image(img_path, opts, OCRResultBuilder())
                
                if page_result.get('result'):
                    page_data = page_result['result']
                    raw_text = page_data.get('raw_text', '')
                    cleaned_text = page_data.get('cleaned_text', '')
                    
                    if raw_text.strip():
                        all_raw_text.append(f"--- Page {i + 1} ---\n{raw_text}")
                    if cleaned_text.strip():
                        all_cleaned_text.append(f"--- Page {i + 1} ---\n{cleaned_text}")
                    
                    total_confidence += page_data.get('metadata', {}).get('ocr_confidence', 0)
                    
                    # Use language info from first page
                    if language_info is None:
                        language_info = page_data.get('language')
                    if preprocessing_info is None:
                        preprocessing_info = page_data.get('metadata', {}).get('preprocessing')
            
            # Combine all text
            combined_raw = '\n\n'.join(all_raw_text)
            combined_cleaned = '\n\n'.join(all_cleaned_text)
            avg_confidence = total_confidence / len(image_paths) if image_paths else 0
            
            logger.info(f"PDF processing complete: {len(image_paths)} pages, {len(combined_raw)} chars")
            
            return result_builder.build(
                raw_text=combined_raw,
                cleaned_text=combined_cleaned,
                transliterated_text=combined_cleaned,  # Use cleaned as transliterated for now
                language_info=language_info or {'detected': 'ur'},
                ocr_confidence=avg_confidence,
                preprocessing_info=preprocessing_info
            )
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            result_builder.add_error(f"PDF processing failed: {e}")
            return result_builder.build(
                raw_text='',
                cleaned_text='',
                transliterated_text='',
                language_info={'detected': 'unknown'},
                ocr_confidence=0,
                preprocessing_info=None
            )
    
    def _process_single_image(self, image_path: str, opts: dict, result_builder) -> dict:
        """Process a single image through the OCR pipeline"""
        preprocessing_info = None
        
        try:
            # Step 1: Image Preprocessing
            if opts['preprocess']:
                stage_start = time.time()
                logger.info("Stage 1: Image preprocessing")
                
                preprocessed_image = self.preprocessor.preprocess(image_path)
                preprocessing_info = self.preprocessor.get_processing_info()
                
                stage_duration = time.time() - stage_start
                result_builder.add_stage(
                    'preprocessing',
                    stage_duration,
                    success=True,
                    data=preprocessing_info
                )
            else:
                preprocessed_image = image_path
                preprocessing_info = None
            
            # Step 2: OCR
            stage_start = time.time()
            logger.info("Stage 2: OCR text extraction")
            
            if opts['use_hybrid_ocr']:
                ocr_result = self.hybrid_ocr.recognize(preprocessed_image)
                raw_text = ocr_result['text']
                ocr_confidence = ocr_result.get('confidence', 0)
                ocr_method = ocr_result.get('method', 'hybrid')
            else:
                ocr_result = self.multilang_ocr.process_image(
                    image_path if not opts['preprocess'] else preprocessed_image,
                    preprocess=False  # Already preprocessed if needed
                )
                raw_text = ocr_result['text']
                ocr_confidence = ocr_result.get('confidence', 0)
                ocr_method = 'tesseract'
            
            stage_duration = time.time() - stage_start
            result_builder.add_stage(
                'ocr',
                stage_duration,
                success=True,
                data={'method': ocr_method, 'confidence': ocr_confidence}
            )
            
            if not raw_text.strip():
                logger.warning("No text extracted from image")
                return result_builder.build(
                    raw_text='',
                    cleaned_text='',
                    transliterated_text='',
                    language_info={'language': 'unknown'},
                    ocr_confidence=0,
                    preprocessing_info=preprocessing_info
                )
            
            # Step 3: Language Detection
            language_info = None
            if opts['detect_language']:
                stage_start = time.time()
                logger.info("Stage 3: Language detection")
                
                language_info = self.language_detector.analyze_text(raw_text)
                
                stage_duration = time.time() - stage_start
                result_builder.add_stage(
                    'language_detection',
                    stage_duration,
                    success=True,
                    data=language_info
                )
            
            # Step 4: Text Cleaning
            cleaned_text = raw_text
            if opts['clean_text']:
                stage_start = time.time()
                logger.info("Stage 4: Text cleaning")
                
                # Use language-specific cleaning if language detected
                if language_info:
                    detected_lang = language_info.get('primary_language', 'en')
                    cleaned_result = self.text_cleaner.clean(raw_text)
                    cleaned_text = self.text_cleaner.clean_by_language(
                        cleaned_result['cleaned'], detected_lang
                    )
                else:
                    cleaned_result = self.text_cleaner.clean(raw_text)
                    cleaned_text = cleaned_result['cleaned']
                
                stage_duration = time.time() - stage_start
                result_builder.add_stage(
                    'cleaning',
                    stage_duration,
                    success=True,
                    data=cleaned_result if 'cleaned_result' in locals() else None
                )
            
            # Step 5: Transliteration
            transliterated_text = None
            if opts['transliterate']:
                stage_start = time.time()
                logger.info("Stage 5: Transliteration")
                
                trans_result = self.transliterator.auto_transliterate(
                    cleaned_text, target_lang='en'
                )
                transliterated_text = trans_result.get('transliterated', cleaned_text)
                
                stage_duration = time.time() - stage_start
                result_builder.add_stage(
                    'transliteration',
                    stage_duration,
                    success=trans_result.get('success', False),
                    data=trans_result
                )
            
            # Build final result
            final_result = result_builder.build(
                raw_text=raw_text,
                cleaned_text=cleaned_text,
                transliterated_text=transliterated_text,
                language_info=language_info,
                ocr_confidence=ocr_confidence,
                preprocessing_info=preprocessing_info
            )
            
            logger.info(f"Pipeline completed successfully in {final_result['processing']['total_time']:.2f}s")
            return final_result
        
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            result_builder.add_error('pipeline', e)
            
            return result_builder.build(
                raw_text='',
                cleaned_text='',
                transliterated_text='',
                language_info={'language': 'unknown'},
                ocr_confidence=0
            )
    
    def batch_process(self, image_paths, options=None):
        """
        Process multiple images
        
        Args:
            image_paths: List of image paths
            options: Processing options
        
        Returns:
            dict: Batch processing results
        """
        logger.info(f"Starting batch processing of {len(image_paths)} images")
        
        start_time = time.time()
        results = []
        
        for idx, image_path in enumerate(image_paths):
            logger.info(f"Processing image {idx + 1}/{len(image_paths)}: {image_path}")
            
            result = self.process(image_path, options)
            result['image_path'] = image_path
            result['image_index'] = idx
            results.append(result)
        
        total_time = time.time() - start_time
        
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        return {
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'total_time': round(total_time, 2),
            'average_time': round(total_time / len(results), 2) if results else 0,
            'results': results
        }
    
    def cleanup(self):
        """Clean up pipeline resources"""
        try:
            self.hybrid_ocr.cleanup()
            logger.info("Pipeline resources cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

def quick_ocr(image_path, preprocess=True, transliterate=True):
    """
    Quick OCR with default settings
    
    Args:
        image_path: Path to image
        preprocess: Whether to preprocess
        transliterate: Whether to transliterate
    
    Returns:
        dict: OCR result
    """
    pipeline = OCRPipeline()
    
    options = {
        'preprocess': preprocess,
        'use_hybrid_ocr': False,
        'clean_text': True,
        'transliterate': transliterate,
        'detect_language': True
    }
    
    return pipeline.process(image_path, options)

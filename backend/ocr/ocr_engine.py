"""
OCR Engine using Tesseract for printed text recognition
Supports English, Hindi, and Urdu languages
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
import logging
import os
from config import Config

logger = logging.getLogger(__name__)

class TesseractOCR:
    """Tesseract-based OCR engine for printed text"""
    
    def __init__(self, tesseract_path=None, languages='eng+hin+urd'):
        """
        Initialize Tesseract OCR
        
        Args:
            tesseract_path: Path to tesseract executable (optional)
            languages: Languages to use (default: English + Hindi + Urdu)
        """
        self.languages = languages
        
        # Set Tesseract path if provided
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif Config.TESSERACT_PATH and os.path.exists(Config.TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
        
        # Set custom tessdata path if available
        if hasattr(Config, 'TESSDATA_PREFIX') and os.path.exists(Config.TESSDATA_PREFIX):
            os.environ['TESSDATA_PREFIX'] = Config.TESSDATA_PREFIX
            logger.info(f"Using tessdata from: {Config.TESSDATA_PREFIX}")
        
        logger.info(f"Initialized Tesseract OCR with languages: {languages}")
        logger.info(f"Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")
    
    def extract_text(self, image_input, config_params=None):
        """
        Extract text from image using Tesseract
        
        Args:
            image_input: Can be file path, PIL Image, or numpy array
            config_params: Custom Tesseract configuration
        
        Returns:
            dict: {
                'text': extracted text,
                'confidence': average confidence score,
                'details': word-level details
            }
        """
        try:
            # Convert input to PIL Image
            if isinstance(image_input, str):
                image = Image.open(image_input)
            elif isinstance(image_input, np.ndarray):
                image = Image.fromarray(image_input)
            else:
                image = image_input
            
            # Default config for better accuracy
            if config_params is None:
                config_params = '--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=self.languages,
                config=config_params
            )
            
            # Get detailed information
            details = pytesseract.image_to_data(
                image,
                lang=self.languages,
                config=config_params,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = []
            for conf in details['conf']:
                # Handle both string and int confidence values
                if isinstance(conf, int):
                    if conf != -1:
                        confidences.append(conf)
                elif isinstance(conf, str) and conf != '-1':
                    try:
                        confidences.append(int(conf))
                    except ValueError:
                        pass
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            logger.info(f"Extracted text with confidence: {avg_confidence:.2f}%")
            
            return {
                'text': text.strip(),
                'confidence': round(avg_confidence, 2),
                'details': details,
                'word_count': len([w for w in details['text'] if w.strip()])
            }
        
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise
    
    def extract_with_boxes(self, image_input):
        """
        Extract text with bounding box coordinates
        
        Args:
            image_input: Image to process
        
        Returns:
            list: List of dicts with text, coordinates, and confidence
        """
        try:
            # Convert input to PIL Image
            if isinstance(image_input, str):
                image = Image.open(image_input)
            elif isinstance(image_input, np.ndarray):
                image = Image.fromarray(image_input)
            else:
                image = image_input
            
            # Get bounding boxes
            boxes = pytesseract.image_to_boxes(
                image,
                lang=self.languages,
                output_type=pytesseract.Output.DICT
            )
            
            # Get detailed data
            data = pytesseract.image_to_data(
                image,
                lang=self.languages,
                output_type=pytesseract.Output.DICT
            )
            
            # Combine results
            results = []
            for i, char in enumerate(boxes['char']):
                if char.strip():
                    results.append({
                        'char': char,
                        'left': boxes['left'][i],
                        'top': boxes['top'][i],
                        'right': boxes['right'][i],
                        'bottom': boxes['bottom'][i]
                    })
            
            return results
        
        except Exception as e:
            logger.error(f"Box extraction failed: {str(e)}")
            raise
    
    def extract_by_language(self, image_input):
        """
        Extract text separately for each language
        
        Args:
            image_input: Image to process
        
        Returns:
            dict: Text extracted for each language
        """
        results = {}
        languages = ['eng', 'hin', 'urd']
        
        for lang in languages:
            try:
                if isinstance(image_input, str):
                    image = Image.open(image_input)
                elif isinstance(image_input, np.ndarray):
                    image = Image.fromarray(image_input)
                else:
                    image = image_input
                
                text = pytesseract.image_to_string(
                    image,
                    lang=lang,
                    config='--oem 3 --psm 6'
                )
                
                results[lang] = text.strip()
            
            except Exception as e:
                logger.warning(f"Failed to extract text for {lang}: {str(e)}")
                results[lang] = ""
        
        return results
    
    def get_available_languages(self):
        """Get list of available Tesseract languages"""
        try:
            languages = pytesseract.get_languages()
            return languages
        except Exception as e:
            logger.error(f"Could not get languages: {str(e)}")
            return []
    
    def check_tesseract_installed(self):
        """Check if Tesseract is properly installed"""
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            return True
        except Exception as e:
            logger.error(f"Tesseract not found: {str(e)}")
            return False

class MultiLanguageOCR:
    """Enhanced OCR with multi-language support and preprocessing"""
    
    def __init__(self):
        self.ocr = TesseractOCR()
        self.supported_languages = {
            'eng': 'English',
            'hin': 'Hindi',
            'urd': 'Urdu'
        }
    
    def process_image(self, image_path, preprocess=True):
        """
        Process image with optional preprocessing
        
        Args:
            image_path: Path to image file
            preprocess: Whether to preprocess image
        
        Returns:
            dict: OCR results with metadata
        """
        from ocr.image_processing import ImagePreprocessor
        
        try:
            # Preprocess if requested
            if preprocess:
                preprocessor = ImagePreprocessor()
                processed_image = preprocessor.preprocess(image_path)
                ocr_result = self.ocr.extract_text(processed_image)
                preprocessing_info = preprocessor.get_processing_info()
            else:
                ocr_result = self.ocr.extract_text(image_path)
                preprocessing_info = {'steps': [], 'total_operations': 0}
            
            return {
                'success': True,
                'text': ocr_result['text'],
                'confidence': ocr_result['confidence'],
                'word_count': ocr_result['word_count'],
                'preprocessing': preprocessing_info,
                'languages_used': self.ocr.languages
            }
        
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0
            }
    
    def batch_process(self, image_paths, preprocess=True):
        """Process multiple images"""
        results = []
        
        for image_path in image_paths:
            result = self.process_image(image_path, preprocess)
            result['image_path'] = image_path
            results.append(result)
        
        return results

def test_ocr_setup():
    """Test if OCR is properly set up"""
    ocr = TesseractOCR()
    
    if not ocr.check_tesseract_installed():
        return {
            'status': 'error',
            'message': 'Tesseract is not installed or not found in PATH'
        }
    
    languages = ocr.get_available_languages()
    required = ['eng', 'hin', 'urd']
    missing = [lang for lang in required if lang not in languages]
    
    if missing:
        return {
            'status': 'warning',
            'message': f'Missing language packs: {", ".join(missing)}',
            'available_languages': languages
        }
    
    return {
        'status': 'success',
        'message': 'OCR is properly configured',
        'available_languages': languages
    }

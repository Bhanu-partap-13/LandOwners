"""
Urdu Handwritten OCR using Transformer models
Handles complex handwritten Urdu text recognition
"""
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

class UrduHandwrittenOCR:
    """Transformer-based OCR for handwritten Urdu text"""
    
    def __init__(self, model_name='microsoft/trocr-base-handwritten'):
        """
        Initialize Urdu handwritten OCR model
        
        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.processor = None
        self.model = None
        self.is_loaded = False
        
        logger.info(f"Initialized Urdu OCR (device: {self.device})")
    
    def load_model(self):
        """Load the transformer model (lazy loading)"""
        if self.is_loaded:
            return
        
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            self.processor = TrOCRProcessor.from_pretrained(self.model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            logger.info("Model loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def recognize_text(self, image_input):
        """
        Recognize handwritten Urdu text from image
        
        Args:
            image_input: PIL Image, numpy array, or file path
        
        Returns:
            dict: Recognition results with text and confidence
        """
        # Load model if not already loaded
        if not self.is_loaded:
            self.load_model()
        
        try:
            # Convert input to PIL Image
            if isinstance(image_input, str):
                image = Image.open(image_input).convert('RGB')
            elif isinstance(image_input, np.ndarray):
                image = Image.fromarray(image_input).convert('RGB')
            else:
                image = image_input.convert('RGB')
            
            # Process image
            pixel_values = self.processor(image, return_tensors='pt').pixel_values
            pixel_values = pixel_values.to(self.device)
            
            # Generate text
            with torch.no_grad():
                generated_ids = self.model.generate(pixel_values)
            
            # Decode text
            generated_text = self.processor.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]
            
            return {
                'text': generated_text.strip(),
                'success': True,
                'model_used': self.model_name
            }
        
        except Exception as e:
            logger.error(f"Recognition failed: {str(e)}")
            return {
                'text': '',
                'success': False,
                'error': str(e)
            }
    
    def batch_recognize(self, images):
        """Process multiple images"""
        results = []
        
        for image in images:
            result = self.recognize_text(image)
            results.append(result)
        
        return results
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.is_loaded:
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            self.is_loaded = False
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Model unloaded")

class HybridOCR:
    """
    Hybrid OCR system that combines Tesseract and Transformer models
    Uses Tesseract for printed text and TrOCR for handwritten text
    """
    
    def __init__(self):
        from ocr.ocr_engine import TesseractOCR
        
        self.tesseract = TesseractOCR()
        self.urdu_ocr = UrduHandwrittenOCR()
        self.loaded = False
    
    def detect_text_type(self, image):
        """
        Detect if text is printed or handwritten
        This is a placeholder - in production, use a classifier model
        
        Args:
            image: Input image
        
        Returns:
            str: 'printed' or 'handwritten'
        """
        # TODO: Implement actual handwritten vs printed classifier
        # For now, we'll try both and use the one with higher confidence
        return 'unknown'
    
    def recognize(self, image_input, force_type=None):
        """
        Recognize text using appropriate OCR method
        
        Args:
            image_input: Image to process
            force_type: Force specific OCR ('printed', 'handwritten', or None for auto)
        
        Returns:
            dict: Recognition results
        """
        if force_type == 'printed':
            result = self.tesseract.extract_text(image_input)
            return {
                'text': result['text'],
                'confidence': result['confidence'],
                'method': 'tesseract',
                'type': 'printed'
            }
        
        elif force_type == 'handwritten':
            result = self.urdu_ocr.recognize_text(image_input)
            return {
                'text': result['text'],
                'confidence': 0,  # TrOCR doesn't provide confidence
                'method': 'trocr',
                'type': 'handwritten'
            }
        
        else:
            # Try both and compare
            tesseract_result = self.tesseract.extract_text(image_input)
            
            # If Tesseract confidence is high, use it
            if tesseract_result['confidence'] > 70:
                return {
                    'text': tesseract_result['text'],
                    'confidence': tesseract_result['confidence'],
                    'method': 'tesseract',
                    'type': 'printed'
                }
            
            # Otherwise, try handwritten OCR
            trocr_result = self.urdu_ocr.recognize_text(image_input)
            
            if trocr_result['success']:
                return {
                    'text': trocr_result['text'],
                    'confidence': 0,
                    'method': 'trocr',
                    'type': 'handwritten'
                }
            
            # Fallback to Tesseract result
            return {
                'text': tesseract_result['text'],
                'confidence': tesseract_result['confidence'],
                'method': 'tesseract',
                'type': 'printed'
            }
    
    def cleanup(self):
        """Clean up resources"""
        self.urdu_ocr.unload_model()

def get_model_info():
    """Get information about available models"""
    return {
        'tesseract': {
            'name': 'Tesseract OCR',
            'languages': ['eng', 'hin', 'urd'],
            'type': 'printed',
            'confidence_available': True
        },
        'trocr': {
            'name': 'TrOCR (Transformer)',
            'model': 'microsoft/trocr-base-handwritten',
            'type': 'handwritten',
            'confidence_available': False
        }
    }

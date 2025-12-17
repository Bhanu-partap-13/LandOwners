"""
Backend Unit Tests
Tests for OCR pipeline components
"""

import pytest
import os
import sys
from PIL import Image
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ocr.image_processing import ImagePreprocessor
from ocr.ocr_engine import TesseractOCR, MultiLanguageOCR
from translation.language_detector import LanguageDetector, SmartLanguageDetector
from common.text_cleaner import TextCleaner, AdvancedTextCleaner
from translation.transliterator import Transliterator
from ocr.confidence_scorer import ConfidenceScorer
from common.performance import CacheManager


# Fixtures
@pytest.fixture
def sample_image():
    """Create a sample test image"""
    img = Image.new('RGB', (800, 600), color='white')
    return np.array(img)


@pytest.fixture
def sample_text():
    """Sample OCR text with common issues"""
    return """
    This is a sample text with    extra   spaces.
    It has some  |  pipe  |  characters.
    And some___underscores___too.
    """


@pytest.fixture
def sample_ocr_result():
    """Sample OCR result for testing"""
    return {
        'raw_text': 'Sample text from OCR',
        'cleaned_text': 'Sample text from OCR',
        'language': {'detected': 'en', 'confidence': 0.95},
        'metadata': {'ocr_confidence': 0.88}
    }


# Image Processing Tests
class TestImagePreprocessor:
    
    def test_initialization(self):
        preprocessor = ImagePreprocessor()
        assert preprocessor is not None
    
    def test_to_grayscale(self, sample_image):
        preprocessor = ImagePreprocessor()
        gray = preprocessor.to_grayscale(sample_image)
        assert len(gray.shape) == 2  # Grayscale has 2 dimensions
    
    def test_denoise(self, sample_image):
        preprocessor = ImagePreprocessor()
        gray = preprocessor.to_grayscale(sample_image)
        denoised = preprocessor.denoise(gray)
        assert denoised is not None
        assert denoised.shape == gray.shape
    
    def test_enhance_contrast(self, sample_image):
        preprocessor = ImagePreprocessor()
        gray = preprocessor.to_grayscale(sample_image)
        enhanced = preprocessor.enhance_contrast(gray)
        assert enhanced is not None
        assert enhanced.shape == gray.shape
    
    def test_binarize(self, sample_image):
        preprocessor = ImagePreprocessor()
        gray = preprocessor.to_grayscale(sample_image)
        binary = preprocessor.binarize(gray)
        assert binary is not None
        # Binary image should only have 0 and 255
        unique_values = np.unique(binary)
        assert len(unique_values) <= 2
    
    def test_full_preprocessing_pipeline(self, sample_image):
        preprocessor = ImagePreprocessor()
        result = preprocessor.preprocess(sample_image)
        assert 'processed_image' in result
        assert 'history' in result
        assert len(result['history']) > 0


# OCR Engine Tests
class TestOCREngine:
    
    def test_tesseract_initialization(self):
        try:
            ocr = TesseractOCR()
            assert ocr is not None
        except Exception as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_multi_language_ocr(self):
        try:
            ocr = MultiLanguageOCR()
            assert ocr is not None
            assert 'eng' in ocr.languages
        except Exception as e:
            pytest.skip(f"Tesseract not available: {e}")


# Language Detection Tests
class TestLanguageDetector:
    
    def test_detect_english(self):
        detector = LanguageDetector()
        result = detector.detect_language("This is an English text")
        assert result['language'] == 'en'
        assert result['confidence'] > 0.8
    
    def test_detect_hindi(self):
        detector = LanguageDetector()
        hindi_text = "यह एक हिंदी पाठ है"
        result = detector.detect_language(hindi_text)
        assert result['language'] == 'hi'
    
    def test_detect_urdu(self):
        detector = LanguageDetector()
        urdu_text = "یہ اردو متن ہے"
        result = detector.detect_language(urdu_text)
        assert result['language'] == 'ur'
    
    def test_smart_detector_script_detection(self):
        detector = SmartLanguageDetector()
        
        # Test Urdu script
        urdu_text = "یہ اردو ہے"
        has_urdu = detector.has_urdu_script(urdu_text)
        assert has_urdu is True
        
        # Test Devanagari script
        hindi_text = "यह हिंदी है"
        has_devanagari = detector.has_devanagari_script(hindi_text)
        assert has_devanagari is True


# Text Cleaner Tests
class TestTextCleaner:
    
    def test_remove_extra_whitespace(self, sample_text):
        cleaner = TextCleaner()
        cleaned = cleaner.remove_extra_whitespace(sample_text)
        assert "    " not in cleaned  # No multiple spaces
    
    def test_remove_unwanted_characters(self):
        cleaner = TextCleaner()
        text = "Text with ||| pipes and ___ underscores"
        cleaned = cleaner.remove_unwanted_characters(text)
        assert "|||" not in cleaned
        assert "___" not in cleaned
    
    def test_full_cleaning(self, sample_text):
        cleaner = TextCleaner()
        cleaned = cleaner.clean(sample_text)
        assert len(cleaned) < len(sample_text)  # Should be shorter after cleaning


# Transliterator Tests
class TestTransliterator:
    
    def test_initialization(self):
        transliterator = Transliterator()
        assert transliterator is not None
    
    def test_urdu_to_roman(self):
        transliterator = Transliterator()
        urdu_text = "سلام"
        result = transliterator.transliterate(urdu_text, 'urdu', 'roman')
        assert result is not None
        assert len(result) > 0


# Confidence Scorer Tests
class TestConfidenceScorer:
    
    def test_initialization(self):
        scorer = ConfidenceScorer()
        assert scorer is not None
    
    def test_calculate_confidence(self, sample_ocr_result):
        scorer = ConfidenceScorer()
        confidence = scorer.calculate_overall_confidence(sample_ocr_result)
        
        assert 'overall' in confidence
        assert 'breakdown' in confidence
        assert 'grade' in confidence
        assert 'recommendations' in confidence
        
        # Score should be between 0 and 1
        assert 0 <= confidence['overall'] <= 1
    
    def test_grade_calculation(self):
        scorer = ConfidenceScorer()
        
        assert scorer._get_grade(0.95) == 'A'
        assert scorer._get_grade(0.85) == 'B'
        assert scorer._get_grade(0.75) == 'C'
        assert scorer._get_grade(0.65) == 'D'
        assert scorer._get_grade(0.50) == 'F'
    
    def test_text_quality_calculation(self):
        scorer = ConfidenceScorer()
        
        # Good quality text
        good_text = "This is a clear and clean text without issues."
        quality = scorer._calculate_text_quality(good_text)
        assert quality > 0.7
        
        # Poor quality text with artifacts
        poor_text = "Text|||with|||many|||artifacts___and___errors"
        quality = scorer._calculate_text_quality(poor_text)
        assert quality < 0.5


# Cache Manager Tests
class TestCacheManager:
    
    def test_initialization(self):
        cache = CacheManager(cache_dir='temp/test_cache')
        assert cache is not None
    
    def test_cache_set_and_get(self):
        cache = CacheManager(cache_dir='temp/test_cache')
        
        test_data = {'result': 'Test data', 'confidence': 0.95}
        cache.set('test.jpg', {'preprocess': True}, test_data)
        
        retrieved = cache.get('test.jpg', {'preprocess': True})
        assert retrieved is not None
        assert retrieved['result'] == test_data['result']
    
    def test_cache_expiration(self):
        import time
        
        # Create cache with very short expiration
        cache = CacheManager(cache_dir='temp/test_cache', max_age_hours=0.0001)
        
        test_data = {'result': 'Test data'}
        cache.set('test.jpg', {}, test_data)
        
        # Wait for expiration
        time.sleep(0.5)
        
        # Should not retrieve expired data
        retrieved = cache.get('test.jpg', {})
        assert retrieved is None


# Integration Tests
class TestIntegration:
    
    def test_full_pipeline_with_sample_image(self, sample_image):
        """Test the full OCR pipeline"""
        # Preprocess
        preprocessor = ImagePreprocessor()
        preprocessed = preprocessor.preprocess(sample_image)
        
        assert preprocessed is not None
        assert 'processed_image' in preprocessed
    
    def test_confidence_scorer_integration(self):
        """Test confidence scoring with realistic data"""
        scorer = ConfidenceScorer()
        
        result = {
            'raw_text': 'Sample land record text with good quality.',
            'cleaned_text': 'Sample land record text with good quality.',
            'language': {'detected': 'en', 'confidence': 0.92},
            'metadata': {'ocr_confidence': 0.88, 'word_count': 7}
        }
        
        confidence = scorer.calculate_overall_confidence(result)
        assert confidence['overall'] > 0.7
        assert confidence['grade'] in ['A', 'B', 'C', 'D', 'F']


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])

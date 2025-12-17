"""
Language detection service for OCR output
Identifies language in extracted text
"""
from langdetect import detect, detect_langs, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import re
import logging

logger = logging.getLogger(__name__)

# Set seed for consistent results
DetectorFactory.seed = 0

class LanguageDetector:
    """Detect language from text"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'ur': 'Urdu',
            'pa': 'Punjabi'
        }
    
    def detect_language(self, text):
        """
        Detect primary language in text
        
        Args:
            text: Input text string
        
        Returns:
            dict: {
                'language': ISO language code,
                'language_name': Full language name,
                'confidence': Detection confidence,
                'is_supported': Whether language is in supported list
            }
        """
        if not text or not text.strip():
            return {
                'language': 'unknown',
                'language_name': 'Unknown',
                'confidence': 0.0,
                'is_supported': False,
                'error': 'Empty text'
            }
        
        try:
            # Detect primary language
            lang_code = detect(text)
            
            # Get confidence scores for all detected languages
            lang_probs = detect_langs(text)
            
            # Get confidence for detected language
            confidence = 0.0
            for lang_prob in lang_probs:
                if lang_prob.lang == lang_code:
                    confidence = lang_prob.prob
                    break
            
            return {
                'language': lang_code,
                'language_name': self.supported_languages.get(lang_code, lang_code.upper()),
                'confidence': round(confidence * 100, 2),
                'is_supported': lang_code in self.supported_languages,
                'all_detected': [
                    {
                        'lang': lp.lang,
                        'prob': round(lp.prob * 100, 2)
                    }
                    for lp in lang_probs
                ]
            }
        
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return {
                'language': 'unknown',
                'language_name': 'Unknown',
                'confidence': 0.0,
                'is_supported': False,
                'error': str(e)
            }
    
    def detect_mixed_language(self, text):
        """
        Detect if text contains multiple languages
        
        Args:
            text: Input text
        
        Returns:
            dict: Information about mixed languages
        """
        if not text or not text.strip():
            return {'is_mixed': False, 'languages': []}
        
        # Split text into sentences/phrases
        sentences = re.split(r'[.!?\n]+', text)
        detected_languages = []
        
        for sentence in sentences:
            if sentence.strip():
                result = self.detect_language(sentence)
                if result['confidence'] > 50:  # Only consider confident detections
                    detected_languages.append(result['language'])
        
        # Count unique languages
        unique_languages = list(set(detected_languages))
        
        return {
            'is_mixed': len(unique_languages) > 1,
            'languages': unique_languages,
            'language_count': len(unique_languages),
            'dominant_language': max(set(detected_languages), key=detected_languages.count) if detected_languages else 'unknown'
        }
    
    def has_urdu_script(self, text):
        """Check if text contains Urdu/Arabic script"""
        # Urdu uses Arabic script with code points in range U+0600 to U+06FF
        urdu_pattern = re.compile(r'[\u0600-\u06FF]')
        return bool(urdu_pattern.search(text))
    
    def has_devanagari_script(self, text):
        """Check if text contains Devanagari script (Hindi)"""
        # Devanagari script range: U+0900 to U+097F
        devanagari_pattern = re.compile(r'[\u0900-\u097F]')
        return bool(devanagari_pattern.search(text))
    
    def detect_script(self, text):
        """
        Detect script type in text
        
        Returns:
            list: Scripts detected in text
        """
        scripts = []
        
        if self.has_urdu_script(text):
            scripts.append('urdu')
        
        if self.has_devanagari_script(text):
            scripts.append('devanagari')
        
        # Check for Latin script (English)
        if re.search(r'[a-zA-Z]', text):
            scripts.append('latin')
        
        return {
            'scripts': scripts,
            'is_multi_script': len(scripts) > 1
        }
    
    def get_text_statistics(self, text):
        """Get statistics about text composition"""
        return {
            'total_chars': len(text),
            'total_words': len(text.split()),
            'latin_chars': len(re.findall(r'[a-zA-Z]', text)),
            'urdu_chars': len(re.findall(r'[\u0600-\u06FF]', text)),
            'devanagari_chars': len(re.findall(r'[\u0900-\u097F]', text)),
            'digits': len(re.findall(r'\d', text)),
            'special_chars': len(re.findall(r'[^\w\s]', text))
        }

class SmartLanguageDetector:
    """Enhanced language detector with script analysis"""
    
    def __init__(self):
        self.detector = LanguageDetector()
    
    def analyze_text(self, text):
        """
        Comprehensive text analysis
        
        Args:
            text: Input text
        
        Returns:
            dict: Complete language and script analysis
        """
        if not text or not text.strip():
            return {
                'error': 'Empty text',
                'language': 'unknown'
            }
        
        # Detect language
        lang_result = self.detector.detect_language(text)
        
        # Detect scripts
        script_result = self.detector.detect_script(text)
        
        # Check for mixed languages
        mixed_result = self.detector.detect_mixed_language(text)
        
        # Get text statistics
        stats = self.detector.get_text_statistics(text)
        
        # Determine best match based on multiple signals
        final_language = self._determine_language(
            lang_result, script_result, stats
        )
        
        return {
            'primary_language': final_language,
            'language_detection': lang_result,
            'script_detection': script_result,
            'mixed_language': mixed_result,
            'statistics': stats,
            'confidence': lang_result.get('confidence', 0)
        }
    
    def _determine_language(self, lang_result, script_result, stats):
        """Determine language using multiple signals"""
        scripts = script_result.get('scripts', [])
        
        # If Urdu script is dominant, likely Urdu
        if 'urdu' in scripts and stats['urdu_chars'] > stats['latin_chars']:
            return 'ur'
        
        # If Devanagari script is dominant, likely Hindi
        if 'devanagari' in scripts and stats['devanagari_chars'] > stats['latin_chars']:
            return 'hi'
        
        # Otherwise use langdetect result
        return lang_result.get('language', 'en')

def test_language_detection():
    """Test language detection"""
    detector = SmartLanguageDetector()
    
    test_texts = {
        'english': 'This is a land record document.',
        'hindi': 'यह एक भूमि रिकॉर्ड दस्तावेज है।',
        'urdu': 'یہ ایک زمینی ریکارڈ دستاویز ہے۔',
        'mixed': 'This document contains یہ mixed languages.'
    }
    
    results = {}
    for label, text in test_texts.items():
        results[label] = detector.analyze_text(text)
    
    return results

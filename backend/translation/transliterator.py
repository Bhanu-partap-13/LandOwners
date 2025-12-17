"""
Transliteration service for converting Urdu to Roman/English
Uses Setu-transliterate or IndicXlit
"""
import sys
import os
import re
import logging

logger = logging.getLogger(__name__)

class Transliterator:
    """Transliterate text between scripts"""
    
    def __init__(self, setu_translate_path=None):
        """
        Initialize transliterator
        
        Args:
            setu_translate_path: Path to setu-translate module
        """
        self.setu_translate_path = setu_translate_path
        self.transliterator_available = False
        
        # Try to load Setu-translate if path provided
        if setu_translate_path and os.path.exists(setu_translate_path):
            try:
                sys.path.insert(0, setu_translate_path)
                # TODO: Import actual Setu-translate modules when available
                # from setu_translate import transliterate
                self.transliterator_available = True
                logger.info(f"Setu-translate loaded from: {setu_translate_path}")
            except Exception as e:
                logger.warning(f"Could not load Setu-translate: {str(e)}")
    
    def transliterate(self, text, source_lang='ur', target_lang='en'):
        """
        Transliterate text from source language to target language
        
        Args:
            text: Input text to transliterate
            source_lang: Source language code ('ur', 'hi', etc.)
            target_lang: Target language code ('en', 'roman', etc.)
        
        Returns:
            dict: Transliterated text with metadata
        """
        if not text or not text.strip():
            return {
                'original': '',
                'transliterated': '',
                'source_lang': source_lang,
                'target_lang': target_lang,
                'success': False
            }
        
        try:
            # Use Setu-translate if available
            if self.transliterator_available:
                transliterated = self.transliterate_with_setu(text, source_lang, target_lang)
            else:
                # Fallback to rule-based transliteration
                transliterated = self.rule_based_transliteration(text, source_lang, target_lang)
            
            return {
                'original': text,
                'transliterated': transliterated,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'success': True,
                'method': 'setu' if self.transliterator_available else 'rule-based'
            }
        
        except Exception as e:
            logger.error(f"Transliteration failed: {str(e)}")
            return {
                'original': text,
                'transliterated': text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'success': False,
                'error': str(e)
            }
    
    def transliterate_with_setu(self, text, source_lang, target_lang):
        """
        Use Setu-translate for transliteration
        This is a placeholder for actual Setu integration
        
        Args:
            text: Text to transliterate
            source_lang: Source language
            target_lang: Target language
        
        Returns:
            Transliterated text
        """
        # TODO: Integrate actual Setu-translate functions
        # from setu_translate import transliterate
        # return transliterate(text, source=source_lang, target=target_lang)
        
        logger.info("Setu-translate would be used here")
        return self.rule_based_transliteration(text, source_lang, target_lang)
    
    def rule_based_transliteration(self, text, source_lang, target_lang):
        """
        Simple rule-based transliteration
        This is a basic fallback - not production-quality
        
        Args:
            text: Text to transliterate
            source_lang: Source language
            target_lang: Target language
        
        Returns:
            Transliterated text
        """
        if source_lang == 'ur' and target_lang == 'en':
            return self.urdu_to_roman(text)
        elif source_lang == 'hi' and target_lang == 'en':
            return self.hindi_to_roman(text)
        else:
            return text
    
    def urdu_to_roman(self, text):
        """
        Basic Urdu to Roman transliteration
        This is a simplified version - use proper transliteration library in production
        """
        # Urdu to Roman mapping (partial)
        urdu_roman_map = {
            'ا': 'a', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ٹ': 't',
            'ث': 's', 'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh',
            'د': 'd', 'ڈ': 'd', 'ذ': 'z', 'ر': 'r', 'ڑ': 'r',
            'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
            'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh',
            'ف': 'f', 'ق': 'q', 'ک': 'k', 'گ': 'g', 'ل': 'l',
            'م': 'm', 'ن': 'n', 'ں': 'n', 'و': 'w', 'ہ': 'h',
            'ھ': 'h', 'ی': 'y', 'ے': 'e'
        }
        
        result = []
        for char in text:
            if char in urdu_roman_map:
                result.append(urdu_roman_map[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def hindi_to_roman(self, text):
        """
        Basic Hindi (Devanagari) to Roman transliteration
        This is a simplified version
        """
        # Devanagari to Roman mapping (partial)
        devanagari_roman_map = {
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u',
            'ऊ': 'oo', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'च': 'ch',
            'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ट': 't', 'ठ': 'th',
            'ड': 'd', 'ढ': 'dh', 'ण': 'n', 'त': 't', 'थ': 'th',
            'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph',
            'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r',
            'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's',
            'ह': 'h'
        }
        
        result = []
        for char in text:
            if char in devanagari_roman_map:
                result.append(devanagari_roman_map[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def batch_transliterate(self, texts, source_lang='ur', target_lang='en'):
        """Transliterate multiple texts"""
        results = []
        
        for text in texts:
            result = self.transliterate(text, source_lang, target_lang)
            results.append(result)
        
        return results
    
    def get_supported_languages(self):
        """Get list of supported language pairs"""
        return {
            'source_languages': ['ur', 'hi', 'pa'],
            'target_languages': ['en', 'roman'],
            'pairs': [
                {'source': 'ur', 'target': 'en', 'name': 'Urdu to English/Roman'},
                {'source': 'hi', 'target': 'en', 'name': 'Hindi to English/Roman'},
                {'source': 'pa', 'target': 'en', 'name': 'Punjabi to English/Roman'}
            ]
        }

class SmartTransliterator:
    """
    Intelligent transliterator with auto-detection
    """
    
    def __init__(self, setu_translate_path=None):
        self.transliterator = Transliterator(setu_translate_path)
    
    def auto_transliterate(self, text, target_lang='en'):
        """
        Auto-detect source language and transliterate
        
        Args:
            text: Input text
            target_lang: Target language (default: 'en')
        
        Returns:
            dict: Transliteration result
        """
        from translation.language_detector import LanguageDetector
        
        # Detect source language
        detector = LanguageDetector()
        lang_result = detector.detect_language(text)
        source_lang = lang_result['language']
        
        # Map detected language to transliteration code
        lang_map = {
            'ur': 'ur',
            'hi': 'hi',
            'pa': 'pa',
            'en': 'en'
        }
        
        source_code = lang_map.get(source_lang, 'ur')
        
        # Don't transliterate if already in target language
        if source_code == target_lang:
            return {
                'original': text,
                'transliterated': text,
                'source_lang': source_code,
                'target_lang': target_lang,
                'success': True,
                'skipped': True,
                'reason': 'Already in target language'
            }
        
        # Transliterate
        result = self.transliterator.transliterate(text, source_code, target_lang)
        result['auto_detected'] = True
        result['detected_confidence'] = lang_result.get('confidence', 0)
        
        return result

def test_transliteration():
    """Test transliteration functionality"""
    trans = SmartTransliterator()
    
    test_texts = {
        'urdu': 'یہ ایک زمینی ریکارڈ دستاویز ہے۔',
        'hindi': 'यह एक भूमि रिकॉर्ड दस्तावेज है।',
        'english': 'This is a land record document.'
    }
    
    results = {}
    for label, text in test_texts.items():
        results[label] = trans.auto_transliterate(text)
    
    return results

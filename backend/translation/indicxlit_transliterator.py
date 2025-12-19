"""
IndicXlit Transliteration Service
=================================
Self-hosted transliteration using AI4Bharat's IndicXlit model.
Converts Indic scripts to Roman/Latin script and vice versa.

Model: IndicXlit (11M params, ~50MB)
- Urdu (Arabic script) → Roman
- Hindi (Devanagari) → Roman
- 21 Indic languages supported

References:
- https://github.com/AI4Bharat/IndicXlit
- https://pypi.org/project/ai4bharat-transliteration/
- Paper: https://arxiv.org/abs/2205.03018
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Lazy loading flags
_xlit_loaded = False
_xlit_engine = None


# Language mappings
XLIT_LANGUAGE_CODES = {
    'ur': 'urd',
    'urdu': 'urd',
    'urd_Arab': 'urd',
    'hi': 'hin',
    'hindi': 'hin',
    'hin_Deva': 'hin',
    'pa': 'pan',
    'punjabi': 'pan',
    'pan_Guru': 'pan',
    'bn': 'ben',
    'bengali': 'ben',
    'ta': 'tam',
    'tamil': 'tam',
    'te': 'tel',
    'telugu': 'tel',
    'mr': 'mar',
    'marathi': 'mar',
    'gu': 'guj',
    'gujarati': 'guj',
    'kn': 'kan',
    'kannada': 'kan',
    'ml': 'mal',
    'malayalam': 'mal',
    'or': 'ori',
    'odia': 'ori',
    'as': 'asm',
    'assamese': 'asm',
    'ks': 'kas',
    'kashmiri': 'kas',
    'sd': 'snd',
    'sindhi': 'snd',
    'ne': 'nep',
    'nepali': 'nep',
    'sa': 'san',
    'sanskrit': 'san',
}


def normalize_xlit_lang(lang: str) -> str:
    """Normalize language code for IndicXlit"""
    lang_lower = lang.lower().strip()
    return XLIT_LANGUAGE_CODES.get(lang_lower, lang_lower[:3])


def is_indicxlit_available() -> bool:
    """Check if IndicXlit is installed"""
    try:
        from ai4bharat.transliteration import XlitEngine
        return True
    except ImportError:
        return False


def load_indicxlit(src_lang: str = 'urd') -> bool:
    """
    Load IndicXlit engine for a specific language
    
    Args:
        src_lang: Source language code (e.g., 'urd', 'hin')
    
    Returns:
        bool: True if loaded successfully
    """
    global _xlit_loaded, _xlit_engine
    
    if _xlit_loaded and _xlit_engine is not None:
        return True
    
    if not is_indicxlit_available():
        logger.warning("IndicXlit not installed. Install with: pip install ai4bharat-transliteration")
        return False
    
    try:
        from ai4bharat.transliteration import XlitEngine
        
        logger.info(f"Loading IndicXlit engine for '{src_lang}'...")
        
        # Initialize with multiple languages for flexibility
        _xlit_engine = XlitEngine(
            src_script_type="indic",
            beam_width=4,
            rescore=False
        )
        
        _xlit_loaded = True
        logger.info("IndicXlit engine loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load IndicXlit: {e}")
        _xlit_loaded = False
        return False


def transliterate_text(
    text: str,
    src_lang: str = 'ur',
    tgt_lang: str = 'en',
    topk: int = 1
) -> Dict:
    """
    Transliterate text from Indic script to Roman
    
    Args:
        text: Text to transliterate
        src_lang: Source language ('ur', 'hi', etc.)
        tgt_lang: Target (usually 'en' for Roman)
        topk: Number of transliteration candidates
    
    Returns:
        dict with transliterated text and metadata
    """
    global _xlit_loaded, _xlit_engine
    
    if not text or not text.strip():
        return {
            'original_text': text,
            'transliterated_text': '',
            'source_lang': src_lang,
            'target_lang': tgt_lang,
            'confidence': 0.0,
            'method': 'empty_input'
        }
    
    src_lang = normalize_xlit_lang(src_lang)
    
    # Try IndicXlit first
    if is_indicxlit_available():
        if not _xlit_loaded:
            load_indicxlit(src_lang)
        
        if _xlit_engine is not None:
            try:
                # Transliterate using IndicXlit
                result = _xlit_engine.translit_sentence(text, src_lang, topk=topk)
                
                # Result is a string (top-1) or list of candidates
                if isinstance(result, list):
                    transliterated = result[0] if result else text
                else:
                    transliterated = result
                
                return {
                    'original_text': text,
                    'transliterated_text': transliterated,
                    'source_lang': src_lang,
                    'target_lang': 'roman',
                    'confidence': 90.0,
                    'method': 'indicxlit',
                    'candidates': result if isinstance(result, list) else [result]
                }
                
            except Exception as e:
                logger.warning(f"IndicXlit transliteration failed: {e}")
    
    # Fallback to rule-based transliteration
    return rule_based_transliteration(text, src_lang)


def rule_based_transliteration(text: str, src_lang: str = 'ur') -> Dict:
    """
    Rule-based transliteration fallback
    
    This provides basic transliteration when IndicXlit is not available.
    Not as accurate as ML-based transliteration but works offline.
    """
    # Urdu (Arabic script) to Roman mapping
    URDU_TO_ROMAN = {
        'ا': 'a', 'آ': 'aa', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ٹ': 't',
        'ث': 's', 'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh',
        'د': 'd', 'ڈ': 'd', 'ذ': 'z', 'ر': 'r', 'ڑ': 'r',
        'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
        'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh',
        'ف': 'f', 'ق': 'q', 'ک': 'k', 'گ': 'g', 'ل': 'l',
        'م': 'm', 'ن': 'n', 'ں': 'n', 'و': 'w', 'ہ': 'h',
        'ھ': 'h', 'ء': "'", 'ی': 'y', 'ے': 'e', 'ئ': 'i',
        # Vowel marks
        'َ': 'a', 'ِ': 'i', 'ُ': 'u', 'ً': 'an', 'ٍ': 'in', 'ٌ': 'un',
        # Numbers (Eastern Arabic numerals)
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        # Common punctuation
        '،': ',', '۔': '.', '؟': '?', '؛': ';',
    }
    
    # Hindi (Devanagari) to Roman mapping
    HINDI_TO_ROMAN = {
        'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u',
        'ऊ': 'oo', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
        'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
        'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
        'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
        'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
        'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
        'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
        'ष': 'sh', 'स': 's', 'ह': 'h',
        # Vowel marks (matras)
        'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
        'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
        'ं': 'n', 'ः': 'h', '्': '',  # Halant
    }
    
    # Select mapping based on source language
    if src_lang in ['ur', 'urd', 'ks', 'kas', 'sd', 'snd']:
        char_map = URDU_TO_ROMAN
    else:
        char_map = HINDI_TO_ROMAN
    
    # Apply character-by-character mapping
    result = []
    for char in text:
        if char in char_map:
            result.append(char_map[char])
        else:
            result.append(char)
    
    transliterated = ''.join(result)
    
    return {
        'original_text': text,
        'transliterated_text': transliterated,
        'source_lang': src_lang,
        'target_lang': 'roman',
        'confidence': 60.0,  # Lower confidence for rule-based
        'method': 'rule_based'
    }


def transliterate_batch(
    texts: List[str],
    src_lang: str = 'ur',
    tgt_lang: str = 'en'
) -> List[str]:
    """
    Transliterate multiple texts
    
    Args:
        texts: List of texts to transliterate
        src_lang: Source language
        tgt_lang: Target language
    
    Returns:
        List of transliterated texts
    """
    results = []
    for text in texts:
        result = transliterate_text(text, src_lang, tgt_lang)
        results.append(result.get('transliterated_text', text))
    return results


class IndicXlitTransliterator:
    """
    High-level transliterator class using IndicXlit
    
    Example:
        xlit = IndicXlitTransliterator()
        result = xlit.transliterate("جموں", src_lang='ur')
        print(result['transliterated_text'])  # 'jammu'
    """
    
    def __init__(self, auto_load: bool = False):
        """
        Initialize transliterator
        
        Args:
            auto_load: If True, load model immediately
        """
        self._loaded = False
        if auto_load:
            self._loaded = load_indicxlit()
    
    def is_available(self) -> bool:
        """Check if IndicXlit is available"""
        return is_indicxlit_available()
    
    def load(self, src_lang: str = 'urd') -> bool:
        """Load the transliteration model"""
        self._loaded = load_indicxlit(src_lang)
        return self._loaded
    
    def transliterate(
        self,
        text: str,
        src_lang: str = 'ur',
        tgt_lang: str = 'en',
        **kwargs
    ) -> Dict:
        """
        Transliterate text from Indic script to Roman
        
        Args:
            text: Text to transliterate
            src_lang: Source language
            tgt_lang: Target language (usually 'en' for Roman)
        
        Returns:
            dict with transliteration result
        """
        return transliterate_text(text, src_lang, tgt_lang)
    
    def transliterate_batch(
        self,
        texts: List[str],
        src_lang: str = 'ur',
        tgt_lang: str = 'en'
    ) -> List[str]:
        """Transliterate multiple texts"""
        return transliterate_batch(texts, src_lang, tgt_lang)
    
    def get_supported_languages(self) -> Dict:
        """Get supported language pairs"""
        return {
            'source_languages': [
                'urd', 'hin', 'ben', 'tam', 'tel', 'mar', 'guj',
                'kan', 'mal', 'pan', 'ori', 'asm', 'kas', 'snd',
                'nep', 'san', 'mai', 'doi', 'sat', 'mni', 'brx', 'gom'
            ],
            'target_languages': ['roman', 'en'],
            'note': 'Also supports Roman to Indic (en → indic) direction'
        }


# Convenience function
def quick_transliterate(text: str, src: str = 'ur') -> str:
    """
    Quick transliterate function
    
    Args:
        text: Text to transliterate
        src: Source language
    
    Returns:
        Transliterated text string
    """
    result = transliterate_text(text, src)
    return result.get('transliterated_text', text)


# Module exports
__all__ = [
    'IndicXlitTransliterator',
    'transliterate_text',
    'transliterate_batch',
    'quick_transliterate',
    'is_indicxlit_available',
    'load_indicxlit',
    'rule_based_transliteration'
]

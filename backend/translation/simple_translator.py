"""
Simple Urdu to English Translator for Land Records
No heavy dependencies (torch, transformers) needed!

Uses comprehensive dictionary-based translation optimized for Jammu land records.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SimpleTranslator:
    """
    Lightweight Urdu to English translator for land records.
    Uses dictionary-based translation with pattern matching.
    """
    
    def __init__(self):
        """Initialize the translator with comprehensive dictionaries"""
        self.initialized = True
        
        # Comprehensive Urdu to English dictionary for land records
        self.urdu_to_english = {
            # Document Types
            'جمع بندی': 'Jamabandi',
            'جمعبندی': 'Jamabandi',
            'فرد': 'Fard',
            'نقشہ': 'Map',
            'انتقال': 'Mutation',
            'رجسٹری': 'Registry',
            'قبضہ': 'Possession',
            'سند': 'Deed',
            'پٹہ': 'Patta/Lease',
            'دستاویز': 'Document',
            
            # Administrative Units
            'موضع': 'Mauza/Village',
            'تحصیل': 'Tehsil',
            'ضلع': 'District',
            'صوبہ': 'Province',
            'پرگنہ': 'Pargana',
            'گاؤں': 'Village',
            'قصبہ': 'Town',
            'محلہ': 'Mohalla',
            'شہر': 'City',
            'بستی': 'Settlement',
            
            # Land Record Specific Terms
            'خسرہ': 'Khasra',
            'کھاتہ': 'Khata',
            'کھیونٹ': 'Khewat',
            'نمبر': 'Number',
            'شجرہ': 'Shajra',
            'پیمائش': 'Survey',
            'حدود': 'Boundaries',
            'مساحت': 'Measurement',
            'رقبہ': 'Area',
            'سال': 'Year',
            'تاریخ': 'Date',
            'صفحہ': 'Page',
            
            # Ownership Terms
            'مالک': 'Owner',
            'مالکان': 'Owners',
            'کاشتکار': 'Cultivator',
            'کاشتکاران': 'Cultivators',
            'مزارع': 'Tenant',
            'شریک': 'Co-sharer',
            'حقدار': 'Claimant',
            'متصرف': 'Possessor',
            'باشندہ': 'Resident',
            'وارث': 'Heir',
            'وارثان': 'Heirs',
            'فروخت کنندہ': 'Seller',
            'خریدار': 'Buyer',
            
            # Area Units
            'ایکڑ': 'Acre',
            'کنال': 'Kanal',
            'مرلہ': 'Marla',
            'بیگھہ': 'Bigha',
            'سرسائی': 'Sarsai',
            'مربع فٹ': 'Square Feet',
            'مربع میٹر': 'Square Meter',
            'گز': 'Gaz/Yard',
            'ہیکٹر': 'Hectare',
            
            # Land Types
            'زمین': 'Land',
            'آبی زمین': 'Irrigated Land',
            'بارانی زمین': 'Rain-fed Land',
            'باغ': 'Orchard',
            'عمارت': 'Building',
            'مکان': 'House',
            'گھر': 'House',
            'دکان': 'Shop',
            'آبپاشی': 'Irrigated',
            'بارانی': 'Rain-fed',
            'بنجر': 'Barren',
            'چراگاہ': 'Pasture',
            'جنگل': 'Forest',
            'نہر': 'Canal',
            'کنواں': 'Well',
            'ٹیوب ویل': 'Tube Well',
            'سڑک': 'Road',
            'راستہ': 'Path',
            'نالا': 'Drain',
            
            # Crop Types
            'فصل': 'Crop',
            'گندم': 'Wheat',
            'چاول': 'Rice',
            'دھان': 'Paddy',
            'مکئی': 'Maize',
            'گنا': 'Sugarcane',
            'کپاس': 'Cotton',
            'سبزیات': 'Vegetables',
            'پھل': 'Fruits',
            
            # Family Relations
            'ولد': 'Son of',
            'والد': 'Father',
            'بنت': 'Daughter of',
            'زوجہ': 'Wife of',
            'بیوہ': 'Widow of',
            'والدہ': 'Mother',
            'بھائی': 'Brother',
            'بہن': 'Sister',
            'چچا': 'Uncle (Paternal)',
            'ماموں': 'Uncle (Maternal)',
            'دادا': 'Grandfather',
            'نواسہ': 'Grandson',
            
            # Common Terms
            'نام': 'Name',
            'کل': 'Total',
            'کل رقبہ': 'Total Area',
            'جنس': 'Type',
            'قسم': 'Category',
            'دستخط': 'Signature',
            'مہر': 'Seal',
            'گواہ': 'Witness',
            'تصدیق': 'Verification',
            'پٹواری': 'Patwari',
            'تحصیلدار': 'Tehsildar',
            'نائب تحصیلدار': 'Naib Tehsildar',
            'قانون گو': 'Qanungo',
            'سرکاری': 'Government',
            'نجی': 'Private',
            'مشترکہ': 'Joint',
            'حصہ': 'Share',
            'حصص': 'Shares',
            'قیمت': 'Price',
            'روپیہ': 'Rupee',
            'لاکھ': 'Lakh',
            'ہزار': 'Thousand',
            
            # Directions
            'شمال': 'North',
            'جنوب': 'South',
            'مشرق': 'East',
            'مغرب': 'West',
            'شمال مشرق': 'North-East',
            'شمال مغرب': 'North-West',
            'جنوب مشرق': 'South-East',
            'جنوب مغرب': 'South-West',
            
            # Status Terms
            'قابل کاشت': 'Cultivable',
            'غیر قابل کاشت': 'Non-cultivable',
            'متروکہ': 'Evacuee',
            'حکومتی': 'Government',
            'محکمانہ': 'Departmental',
            
            # Jammu & Kashmir Specific Places
            'اتما پور': 'Atmapur',
            'آتما پور': 'Atmapur',
            'بشنال': 'Bishnah',
            'بشناہ': 'Bishnah',
            'جموں': 'Jammu',
            'جامو': 'Jammu',
            'کٹھوعہ': 'Kathua',
            'اودھمپور': 'Udhampur',
            'سامبا': 'Samba',
            'راجوری': 'Rajouri',
            'پونچھ': 'Poonch',
            'ڈوڈہ': 'Doda',
            'رامبن': 'Ramban',
            'کشتواڑ': 'Kishtwar',
            'ریاسی': 'Reasi',
            'سرینگر': 'Srinagar',
            'انند ناگ': 'Anantnag',
            'بارہمولہ': 'Baramulla',
            'کپواڑہ': 'Kupwara',
            'بڈگام': 'Budgam',
            'پلوامہ': 'Pulwama',
            'شوپیاں': 'Shopian',
            'کلگام': 'Kulgam',
            'بانڈی پورہ': 'Bandipora',
            'گندربل': 'Ganderbal',
            'لیہ': 'Leh',
            'کارگل': 'Kargil',
            
            # Additional Common Words
            'اور': 'and',
            'یا': 'or',
            'سے': 'from',
            'تک': 'to/until',
            'کا': 'of',
            'کی': 'of',
            'کے': 'of',
            'میں': 'in',
            'پر': 'on',
            'ہے': 'is',
            'ہیں': 'are',
            'تھا': 'was',
            'تھے': 'were',
            'بعد': 'after',
            'پہلے': 'before',
            'بمطابق': 'according to',
            'مطابق': 'according',
            'مندرجہ': 'mentioned',
            'بالا': 'above',
            'ذیل': 'below',
            'مذکورہ': 'stated',
            
            # Numbers (Urdu numerals)
            '۰': '0',
            '۱': '1',
            '۲': '2',
            '۳': '3',
            '۴': '4',
            '۵': '5',
            '۶': '6',
            '۷': '7',
            '۸': '8',
            '۹': '9',
        }
        
        # Common number words
        self.number_words = {
            'ایک': '1',
            'دو': '2',
            'تین': '3',
            'چار': '4',
            'پانچ': '5',
            'چھ': '6',
            'سات': '7',
            'آٹھ': '8',
            'نو': '9',
            'دس': '10',
            'گیارہ': '11',
            'بارہ': '12',
            'تیرہ': '13',
            'چودہ': '14',
            'پندرہ': '15',
            'سولہ': '16',
            'سترہ': '17',
            'اٹھارہ': '18',
            'انیس': '19',
            'بیس': '20',
            'سو': '100',
        }
        
        # Add number words to main dictionary
        self.urdu_to_english.update(self.number_words)
        
        # Sort dictionary by length (longer phrases first for better matching)
        self._sorted_keys = sorted(self.urdu_to_english.keys(), key=len, reverse=True)
        
        logger.info(f"SimpleTranslator initialized with {len(self.urdu_to_english)} terms")
    
    def translate(
        self,
        text: str,
        src_lang: str = 'ur',
        tgt_lang: str = 'en'
    ) -> str:
        """
        Translate text from Urdu to English
        
        Args:
            text: Text to translate
            src_lang: Source language (default: ur)
            tgt_lang: Target language (default: en)
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return ""
        
        translated = text
        
        # Replace known terms (longer phrases first)
        for urdu_term in self._sorted_keys:
            if urdu_term in translated:
                translated = translated.replace(urdu_term, self.urdu_to_english[urdu_term])
        
        # Clean up whitespace
        translated = ' '.join(translated.split())
        
        return translated
    
    def translate_text(
        self,
        text: str,
        source_lang: str = 'ur',
        target_lang: str = 'en'
    ) -> Dict:
        """
        Translate text with full metadata response
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dictionary with translated text and metadata
        """
        if not text or not text.strip():
            return {
                'translated_text': '',
                'source_language': source_lang,
                'target_language': target_lang,
                'confidence': 0.0,
                'method': 'none'
            }
        
        translated = self.translate(text, source_lang, target_lang)
        
        # Calculate confidence based on how much was translated
        original_urdu_chars = len([c for c in text if '\u0600' <= c <= '\u06FF'])
        remaining_urdu_chars = len([c for c in translated if '\u0600' <= c <= '\u06FF'])
        
        if original_urdu_chars > 0:
            translation_ratio = 1 - (remaining_urdu_chars / original_urdu_chars)
            confidence = min(0.95, 0.5 + (translation_ratio * 0.45))
        else:
            confidence = 0.9  # Already English or no Urdu
        
        return {
            'translated_text': translated,
            'source_language': source_lang,
            'target_language': target_lang,
            'confidence': round(confidence, 2),
            'method': 'dictionary-based'
        }
    
    def translate_batch(
        self,
        texts: List[str],
        src_lang: str = 'ur',
        tgt_lang: str = 'en'
    ) -> List[str]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            src_lang: Source language
            tgt_lang: Target language
            
        Returns:
            List of translated texts
        """
        return [self.translate(text, src_lang, tgt_lang) for text in texts]
    
    def translate_document(
        self,
        text: str,
        src_lang: str = 'ur',
        tgt_lang: str = 'en',
        preserve_structure: bool = True
    ) -> Dict:
        """
        Translate a document while preserving structure
        
        Args:
            text: Document text
            src_lang: Source language
            tgt_lang: Target language
            preserve_structure: Whether to preserve line/paragraph structure
            
        Returns:
            Dictionary with original, translated text and metadata
        """
        if not text or not text.strip():
            return {
                'original_text': text,
                'translated_text': '',
                'source_language': src_lang,
                'target_language': tgt_lang,
                'method': 'none',
                'confidence': 0.0
            }
        
        if preserve_structure:
            # Translate line by line to preserve structure
            lines = text.split('\n')
            translated_lines = []
            
            for line in lines:
                if line.strip():
                    translated_lines.append(self.translate(line.strip(), src_lang, tgt_lang))
                else:
                    translated_lines.append('')
            
            translated_text = '\n'.join(translated_lines)
        else:
            translated_text = self.translate(text, src_lang, tgt_lang)
        
        # Calculate overall confidence
        result = self.translate_text(text, src_lang, tgt_lang)
        
        return {
            'original_text': text,
            'translated_text': translated_text,
            'source_language': src_lang,
            'target_language': tgt_lang,
            'method': 'dictionary-based',
            'confidence': result['confidence']
        }
    
    def add_custom_terms(self, terms: Dict[str, str]):
        """
        Add custom translation terms
        
        Args:
            terms: Dictionary of Urdu -> English mappings
        """
        self.urdu_to_english.update(terms)
        self._sorted_keys = sorted(self.urdu_to_english.keys(), key=len, reverse=True)
        logger.info(f"Added {len(terms)} custom terms. Total: {len(self.urdu_to_english)}")
    
    def get_term_count(self) -> int:
        """Get number of terms in dictionary"""
        return len(self.urdu_to_english)
    
    def is_available(self) -> bool:
        """Check if translator is available (always True for this simple version)"""
        return True


# Create singleton instance
_translator_instance = None

def get_translator() -> SimpleTranslator:
    """Get or create translator instance"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = SimpleTranslator()
    return _translator_instance


def translate_urdu_to_english(text: str) -> str:
    """
    Quick function to translate Urdu to English
    
    Args:
        text: Urdu text
        
    Returns:
        English translation
    """
    translator = get_translator()
    return translator.translate(text)


# Test function
def test_simple_translator():
    """Test the simple translator"""
    translator = SimpleTranslator()
    
    test_texts = [
        "جمع بندی موضع اتما پور تحصیل بشنال ضلع جموں",
        "خسرہ نمبر ۱۲۳",
        "مالک نام: محمد احمد ولد عبدالله",
        "رقبہ: ۵ کنال ۱۰ مرلہ",
        "زمین کی قسم: آبپاشی",
        "فصل: گندم",
    ]
    
    print("=" * 60)
    print("Testing Simple Urdu-English Translator")
    print("=" * 60)
    
    for text in test_texts:
        result = translator.translate_text(text)
        print(f"\nInput:      {text}")
        print(f"Output:     {result['translated_text']}")
        print(f"Confidence: {result['confidence']}")
    
    print("\n" + "=" * 60)
    print(f"Dictionary contains {translator.get_term_count()} terms")
    print("=" * 60)


if __name__ == '__main__':
    test_simple_translator()

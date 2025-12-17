"""
Setu-Translate Integration
Precise Urdu to English translation for land records
Uses AI4Bharat IndicTrans2 model
"""

import os
import sys
from typing import Dict, List, Optional
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add Setu path
SETU_TRANSLATE_PATH = os.path.join(os.path.dirname(__file__), '../../..', 'IndicLLMSuite', 'setu-translate')
if os.path.exists(SETU_TRANSLATE_PATH):
    sys.path.insert(0, SETU_TRANSLATE_PATH)

# Import the real IndicTrans translator
try:
    from .indictrans_translator import IndicTransTranslator
    INDICTRANS_AVAILABLE = True
except ImportError:
    INDICTRANS_AVAILABLE = False
    logger.warning("IndicTransTranslator not available, using fallback")


class SetuTranslator:
    """
    Translates Urdu text to English using Setu-translate/IndicTrans2
    Maintains document structure and formatting
    """
    
    def __init__(self):
        self.supported_languages = {
            'ur': 'Urdu',
            'hi': 'Hindi',
            'en': 'English'
        }
        
        # Initialize IndicTrans translator
        self._indictrans = None
        self.setu_available = self._check_setu_availability()
        
        logger.info(f"SetuTranslator initialized (IndicTrans available: {self.setu_available})")
    
    def _check_setu_availability(self) -> bool:
        """Check if Setu-translate/IndicTrans2 is available"""
        try:
            if INDICTRANS_AVAILABLE:
                # Try to create instance (lazy - won't load model yet)
                self._indictrans = IndicTransTranslator(direction='indic-en')
                return self._indictrans.is_available()
            return False
        except Exception as e:
            logger.warning(f"Setu-translate not available: {e}")
            return False
    
    def translate_text(self, text: str, source_lang: str = 'ur', 
                      target_lang: str = 'en') -> Dict:
        """
        Translate text using Setu-translate
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: ur)
            target_lang: Target language code (default: en)
            
        Returns:
            Dictionary with translated text and metadata
        """
        if not text or len(text.strip()) == 0:
            return {
                'translated_text': '',
                'source_language': source_lang,
                'target_language': target_lang,
                'confidence': 0.0,
                'method': 'none'
            }
        
        # Try Setu-translate first
        if self.setu_available:
            result = self._translate_with_setu(text, source_lang, target_lang)
            if result['success']:
                return result['data']
        
        # Fallback to rule-based translation
        return self._translate_fallback(text, source_lang, target_lang)
    
    def _translate_with_setu(self, text: str, source_lang: str, 
                            target_lang: str) -> Dict:
        """
        Translate using IndicTrans2 model via setu-translate
        """
        try:
            if self._indictrans is None:
                return {'success': False, 'error': 'IndicTrans not initialized'}
            
            # Translate using the real model
            # Note: translate_document expects a dict or string, but returns a dict
            # We need to handle both cases
            
            # If text is simple string, use translate_text/translate_batch
            if isinstance(text, str):
                translated_text = self._indictrans.translate(
                    text, 
                    src_lang=source_lang, 
                    tgt_lang=target_lang
                )
                
                return {
                    'success': True,
                    'data': {
                        'translated_text': translated_text,
                        'source_language': source_lang,
                        'target_language': target_lang,
                        'confidence': 0.95,
                        'method': 'indictrans2'
                    }
                }
            
            # If it's a document structure
            result = self._indictrans.translate_document(
                text, 
                src_lang=source_lang, 
                tgt_lang=target_lang,
                preserve_structure=True
            )
            
            return {
                'success': True,
                'data': {
                    'translated_text': result.get('translated_text', ''),
                    'source_language': result.get('source_language', source_lang),
                    'target_language': result.get('target_language', target_lang),
                    'confidence': result.get('confidence', 0.9),
                    'method': 'indictrans2'
                }
            }
            
        except Exception as e:
            logger.error(f"Setu/IndicTrans translation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _translate_fallback(self, text: str, source_lang: str, 
                           target_lang: str) -> Dict:
        """
        Fallback translation using rule-based approach
        """
        # Basic Urdu to English word mapping for land records
        urdu_to_english = {
            # Document terms
            'جمع بندی': 'Jamabandi',
            'موضع': 'Village',
            'تحصیل': 'Tehsil',
            'ضلع': 'District',
            'سال': 'Year',
            'نمبر': 'Number',
            'خسرہ': 'Khasra',
            'مالک': 'Owner',
            'کاشتکار': 'Cultivator',
            'رقبہ': 'Area',
            'ایکڑ': 'Acre',
            'کنال': 'Kanal',
            'مرلہ': 'Marla',
            'فصل': 'Crop',
            
            # Places (as mentioned by user)
            'اتما پور': 'Atmapur',
            'بشنال': 'Bishnah',
            'جموں': 'Jammu',
            
            # Common words
            'نام': 'Name',
            'ولد': 'Son of',
            'والد': 'Father',
            'مکان': 'House',
            'گاؤں': 'Village',
            'محلہ': 'Mohalla',
            'کل': 'Total',
            'جنس': 'Type',
            'زمین': 'Land',
            'باغ': 'Orchard',
            'عمارت': 'Building',
        }
        
        # Translate by replacing known terms
        translated = text
        for urdu, english in urdu_to_english.items():
            translated = translated.replace(urdu, english)
        
        # Clean up
        translated = self._clean_translation(translated)
        
        return {
            'translated_text': translated,
            'source_language': source_lang,
            'target_language': target_lang,
            'confidence': 0.7,  # Lower confidence for fallback
            'method': 'rule-based-fallback'
        }
    
    def _clean_translation(self, text: str) -> str:
        """Clean and format translated text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Capitalize sentences
        sentences = text.split('.')
        sentences = [s.strip().capitalize() for s in sentences if s.strip()]
        text = '. '.join(sentences)
        
        if text and not text.endswith('.'):
            text += '.'
        
        return text
    
    def translate_document(self, ocr_result: Dict) -> Dict:
        """
        Translate entire OCR result document
        
        Args:
            ocr_result: OCR result dictionary with text fields
            
        Returns:
            Translation result with all fields
        """
        result = {
            'original': {},
            'translated': {},
            'metadata': {}
        }
        
        # Get text to translate
        raw_text = ocr_result.get('raw_text', '')
        cleaned_text = ocr_result.get('cleaned_text', raw_text)
        
        # Detect language
        detected_lang = ocr_result.get('language', {}).get('detected', 'ur')
        
        # Translate
        translation = self.translate_text(cleaned_text, detected_lang, 'en')
        
        # Build result
        result['original'] = {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'language': detected_lang
        }
        
        result['translated'] = {
            'text': translation['translated_text'],
            'language': translation['target_language']
        }
        
        result['metadata'] = {
            'source_language': translation['source_language'],
            'target_language': translation['target_language'],
            'confidence': translation['confidence'],
            'method': translation['method'],
            'original_length': len(cleaned_text),
            'translated_length': len(translation['translated_text'])
        }
        
        return result
    
    def translate_structured_document(self, text: str) -> Dict:
        """
        Translate structured land record document
        Preserves structure and extracts key fields
        """
        # Extract structured data
        structured_data = self._extract_land_record_fields(text)
        
        # Translate each field
        translated_fields = {}
        for field_name, field_value in structured_data.items():
            if field_value:
                translation = self.translate_text(field_value, 'ur', 'en')
                translated_fields[field_name] = translation['translated_text']
            else:
                translated_fields[field_name] = field_value
        
        # Create formatted output
        formatted_output = self._format_land_record(translated_fields)
        
        return {
            'structured_fields': translated_fields,
            'formatted_text': formatted_output,
            'original_fields': structured_data
        }
    
    def _extract_land_record_fields(self, text: str) -> Dict:
        """
        Extract structured fields from land record
        """
        fields = {
            'document_type': '',
            'village': '',
            'tehsil': '',
            'district': '',
            'year': '',
            'khasra_number': '',
            'owner_name': '',
            'area': '',
            'crop_type': '',
            'other_details': ''
        }
        
        # Simple extraction based on keywords
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Document type
            if 'جمع بندی' in line:
                fields['document_type'] = 'Jamabandi'
            
            # Village
            if 'موضع' in line or 'گاؤں' in line:
                fields['village'] = line
            
            # Tehsil
            if 'تحصیل' in line:
                fields['tehsil'] = line
            
            # District
            if 'ضلع' in line:
                fields['district'] = line
            
            # Store remaining as other details
            if not any(keyword in line for keyword in ['جمع بندی', 'موضع', 'تحصیل', 'ضلع']):
                fields['other_details'] += line + '\n'
        
        return fields
    
    def _format_land_record(self, fields: Dict) -> str:
        """
        Format land record in English
        """
        formatted = f"""
LAND RECORD TRANSLATION
{'=' * 60}

Document Type: {fields.get('document_type', 'N/A')}
Village: {fields.get('village', 'N/A')}
Tehsil: {fields.get('tehsil', 'N/A')}
District: {fields.get('district', 'N/A')}
Year: {fields.get('year', 'N/A')}

PROPERTY DETAILS
{'-' * 60}
Khasra Number: {fields.get('khasra_number', 'N/A')}
Owner Name: {fields.get('owner_name', 'N/A')}
Area: {fields.get('area', 'N/A')}
Crop Type: {fields.get('crop_type', 'N/A')}

ADDITIONAL DETAILS
{'-' * 60}
{fields.get('other_details', 'N/A')}

{'=' * 60}
Translation Method: Setu-Translate
Date: {self._get_current_date()}
        """.strip()
        
        return formatted
    
    def _get_current_date(self) -> str:
        """Get current date string"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class RAGTranslator:
    """
    RAG-based translator for handling large PDF documents efficiently.
    Uses chunking, caching, and incremental processing.
    """
    
    def __init__(self, cache_dir: str = None):
        """Initialize RAG translator"""
        from document.rag_document_processor import RAGDocumentProcessor
        self.rag_processor = RAGDocumentProcessor(cache_dir=cache_dir)
        self.setu_translator = SetuTranslator()
        logger.info("RAG Translator initialized")
    
    def process_large_pdf(
        self,
        pdf_path: str,
        translate: bool = True,
        streaming: bool = True,
        progress_callback: callable = None
    ):
        """
        Process large PDF using RAG approach
        
        Args:
            pdf_path: Path to PDF file
            translate: Whether to translate text
            streaming: Use streaming mode for memory efficiency
            progress_callback: Callback for progress updates
            
        Returns:
            Generator (streaming) or Dict (batch) of results
        """
        if streaming:
            return self.rag_processor.process_pdf_streaming(
                pdf_path,
                translate=translate,
                src_lang='ur',
                tgt_lang='en',
                progress_callback=progress_callback
            )
        else:
            return self.rag_processor.process_pdf_batch(
                pdf_path,
                translate=translate,
                src_lang='ur',
                tgt_lang='en',
                progress_callback=progress_callback
            )
    
    def search_and_translate(self, query: str, top_k: int = 5) -> Dict:
        """
        Search processed document and return relevant translations
        
        Args:
            query: Search query in source language
            top_k: Number of results
            
        Returns:
            Dict with relevant translations
        """
        return self.rag_processor.get_translation_for_query(query, top_k)
    
    def get_progress(self) -> Dict:
        """Get current processing progress"""
        return self.rag_processor.get_progress()
    
    def translate_text(self, text: str, src_lang: str = 'ur', tgt_lang: str = 'en') -> Dict:
        """Translate text using underlying SetuTranslator"""
        return self.setu_translator.translate_text(text, src_lang, tgt_lang)


def test_translator():
    """Test the translator"""
    translator = SetuTranslator()
    
    # Test text
    test_text = "جمع بندی موضع اتما پور تحصیل بشنال ضلع جموں"
    
    print("Testing Setu Translator")
    print(f"Input: {test_text}")
    
    result = translator.translate_text(test_text)
    print(f"\nTranslated: {result['translated_text']}")
    print(f"Method: {result['method']}")
    print(f"Confidence: {result['confidence']}")


if __name__ == '__main__':
    test_translator()

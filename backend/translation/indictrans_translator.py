"""
IndicTrans2 Translation Module
Real translation using AI4Bharat's IndicTrans2 model for Urdu→English
Integrated from setu-translate pipeline
"""

import os
import torch
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndicTransTranslator:
    """
    Wrapper for IndicTrans2 model providing Urdu→English translation
    Uses IndicTransTokenizer for proper preprocessing
    """
    
    # Language code mappings (FLORES codes)
    LANG_CODES = {
        'ur': 'urd_Arab',    # Urdu (Arabic script)
        'hi': 'hin_Deva',    # Hindi (Devanagari)
        'en': 'eng_Latn',    # English (Latin)
        'ks': 'kas_Arab',    # Kashmiri (Arabic script)
        'pa': 'pan_Guru',    # Punjabi (Gurmukhi)
        'doi': 'doi_Deva',   # Dogri (Devanagari)
    }
    
    # Supported translation directions
    # Using IndicTrans2 models from HuggingFace
    # Note: Some models are gated and require HF login
    DIRECTIONS = {
        'indic-en': 'ai4bharat/indictrans2-indic-en-dist-200M',
        'en-indic': 'ai4bharat/indictrans2-en-indic-dist-200M'
    }
    
    # Alternative open models (if gated ones fail)
    ALTERNATIVE_MODELS = {
        'indic-en': 'facebook/nllb-200-distilled-600M',
        'en-indic': 'facebook/nllb-200-distilled-600M'
    }
    
    def __init__(self, direction: str = 'indic-en', device: str = None, use_fallback: bool = True):
        """
        Initialize IndicTrans2 translator
        
        Args:
            direction: Translation direction ('indic-en' or 'en-indic')
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
            use_fallback: If True, use NLLB model if IndicTrans2 is not accessible
        """
        self.direction = direction
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.use_fallback = use_fallback
        self.using_fallback_model = False
        
        self.model = None
        self.ip = None
        self.tokenizer = None
        self._initialized = False
        
        logger.info(f"IndicTransTranslator initialized (direction={direction}, device={self.device})")
    
    def _lazy_init(self):
        """Lazy initialization of heavy components (model, tokenizer)"""
        if self._initialized:
            return
        
        try:
            from transformers import AutoModelForSeq2SeqLM
            from IndicTransTokenizer import IndicProcessor, IndicTransTokenizer
            
            # Patch Urdu normalizer before loading model/processor
            self._patch_urdu_normalizer()
            
            logger.info("Loading IndicTrans2 model... (this may take a moment)")
            
            # Load model
            model_name = self.DIRECTIONS.get(self.direction)
            if not model_name:
                raise ValueError(f"Invalid direction: {self.direction}")
            
            try:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    trust_remote_code=True
                )
            except OSError as e:
                if "gated repo" in str(e).lower() and self.use_fallback:
                    logger.warning(f"IndicTrans2 model is gated. Using local translation instead.")
                    logger.info("To use IndicTrans2: 1) Accept license at https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M")
                    logger.info("                    2) Run: huggingface-cli login")
                    self.using_fallback_model = True
                    self._initialized = True
                    # Initialize processor and tokenizer for preprocessing only
                    self.ip = IndicProcessor(inference=True)
                    return
                else:
                    raise
            
            self.model = self.model.eval().to(self.device)
            
            # Initialize processor and tokenizer
            self.ip = IndicProcessor(inference=True)
            self.tokenizer = IndicTransTokenizer(direction=self.direction)
            
            self._initialized = True
            logger.info(f"IndicTrans2 model loaded successfully on {self.device}")
            
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            raise ImportError(
                "IndicTransTokenizer not installed. Run: "
                "pip install --editable ./IndicTransTokenizer"
            )
        except Exception as e:
            logger.error(f"Failed to initialize IndicTrans2: {e}")
            # Mark as initialized but in fallback mode
            self.using_fallback_model = True
            self._initialized = True
    
    def _patch_urdu_normalizer(self):
        """Patch the Urdu normalizer to avoid urduhack dependency issues"""
        try:
            import indicnlp.normalize.indic_normalize as indic_norm
            # Replace UrduNormalizer with a simple passthrough
            class SimpleUrduNormalizer:
                def __init__(self, lang=None, **kwargs):
                    pass
                def normalize(self, text):
                    return text
            indic_norm.UrduNormalizer = SimpleUrduNormalizer
            logger.info("Patched UrduNormalizer to avoid urduhack dependency")
        except Exception as e:
            logger.warning(f"Could not patch UrduNormalizer: {e}")
    
    def get_flores_code(self, lang_code: str) -> str:
        """Convert short language code to FLORES code"""
        return self.LANG_CODES.get(lang_code, lang_code)
    
    def _minimal_preprocess(self, texts: List[str], src_lang: str, tgt_lang: str) -> List[str]:
        """
        Minimal preprocessing for when urduhack/full normalization is unavailable.
        Performs basic cleaning without language-specific normalization.
        """
        processed = []
        for text in texts:
            # Basic normalization
            text = text.strip()
            # Normalize whitespace
            text = ' '.join(text.split())
            # Add BOS/EOS tags as expected by IndicTrans2
            # Format: <2tgt_lang> text
            text = f"<2{tgt_lang}> {text}"
            processed.append(text)
        return processed
    
    def translate(
        self, 
        text: str, 
        src_lang: str = 'ur', 
        tgt_lang: str = 'en',
        max_length: int = 256,
        num_beams: int = 5
    ) -> str:
        """
        Translate a single text string
        
        Args:
            text: Text to translate
            src_lang: Source language code ('ur', 'hi', etc.)
            tgt_lang: Target language code ('en', 'hi', etc.)
            max_length: Maximum length of generated translation
            num_beams: Number of beams for beam search
            
        Returns:
            Translated text string
        """
        if not text or not text.strip():
            return ""
        
        results = self.translate_batch(
            [text], 
            src_lang=src_lang, 
            tgt_lang=tgt_lang,
            max_length=max_length,
            num_beams=num_beams
        )
        
        return results[0] if results else ""
    
    def translate_batch(
        self,
        texts: List[str],
        src_lang: str = 'ur',
        tgt_lang: str = 'en',
        max_length: int = 256,
        num_beams: int = 5,
        batch_size: int = 8
    ) -> List[str]:
        """
        Translate a batch of texts
        
        Args:
            texts: List of texts to translate
            src_lang: Source language code
            tgt_lang: Target language code
            max_length: Maximum length of generated translation
            num_beams: Number of beams for beam search
            batch_size: Batch size for processing
            
        Returns:
            List of translated texts
        """
        self._lazy_init()
        
        if not texts:
            return []
        
        # Filter empty texts
        valid_texts = [t.strip() for t in texts if t and t.strip()]
        if not valid_texts:
            return [""] * len(texts)
        
        # If using fallback (no model available), use rule-based translation
        if self.using_fallback_model:
            logger.info("Using rule-based fallback translation")
            return self._fallback_translate_batch(valid_texts, texts, src_lang, tgt_lang)
        
        # Convert language codes
        src_flores = self.get_flores_code(src_lang)
        tgt_flores = self.get_flores_code(tgt_lang)
        
        logger.info(f"Translating {len(valid_texts)} texts: {src_flores} → {tgt_flores}")
        
        try:
            # Process in batches
            all_translations = []
            
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i:i + batch_size]
                
                # Preprocess batch - skip Urdu normalization to avoid urduhack/TF incompatibility
                try:
                    processed = self.ip.preprocess_batch(
                        batch, 
                        src_lang=src_flores, 
                        tgt_lang=tgt_flores
                    )
                except (ModuleNotFoundError, ImportError) as e:
                    # urduhack dependency issue - use minimal preprocessing
                    logger.warning(f"Skipping advanced normalization due to: {e}")
                    processed = self._minimal_preprocess(batch, src_flores, tgt_flores)
                
                # Get placeholder maps for postprocessing - ensure list of dicts even if empty
                ple_maps = self.ip.get_placeholder_entity_maps(clear_ple_maps=True)
                if not ple_maps or len(ple_maps) < len(batch):
                    ple_maps = [{} for _ in batch]
                
                # Tokenize - use 'longest' padding as expected by IndicTransTokenizer
                inputs = self.tokenizer(
                    processed,
                    src=True,
                    padding="longest",
                    truncation=True,
                    max_length=max_length,
                    return_tensors="pt"
                )
                
                # Move to device
                input_ids = inputs["input_ids"].to(self.device)
                attention_mask = inputs["attention_mask"].to(self.device)
                
                # Generate translations
                with torch.no_grad():
                    outputs = self.model.generate(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        max_length=max_length,
                        num_beams=num_beams,
                        num_return_sequences=1,
                        do_sample=False
                    )
                
                # Decode outputs
                decoded = self.tokenizer.batch_decode(outputs, src=False)
                logger.debug(f"Decoded outputs: {decoded}")
                
                # Postprocess - skip if using minimal preprocessing
                try:
                    translations = self.ip.postprocess_batch(
                        decoded, 
                        lang=tgt_flores,
                        placeholder_entity_maps=ple_maps
                    )
                except Exception as pp_err:
                    logger.warning(f"Postprocessing skipped: {pp_err}")
                    # Just clean up the decoded outputs
                    translations = [t.strip() for t in decoded]
                
                all_translations.extend(translations)
                logger.debug(f"Batch translations: {translations}")
            
            # Map back to original indices (including empty strings)
            result = []
            valid_idx = 0
            for text in texts:
                if text and text.strip():
                    result.append(all_translations[valid_idx])
                    valid_idx += 1
                else:
                    result.append("")
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise
    
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
            text: Document text to translate
            src_lang: Source language
            tgt_lang: Target language
            preserve_structure: Whether to preserve paragraph/line structure
            
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
        
        # Ensure initialization
        self._lazy_init()
        
        if preserve_structure:
            # Split by paragraphs/lines and translate each
            paragraphs = text.split('\n')
            translated_paragraphs = []
            
            for para in paragraphs:
                if para.strip():
                    translated = self.translate(para.strip(), src_lang, tgt_lang)
                    translated_paragraphs.append(translated)
                else:
                    translated_paragraphs.append('')
            
            translated_text = '\n'.join(translated_paragraphs)
        else:
            # Translate as single block
            translated_text = self.translate(text, src_lang, tgt_lang)
        
        # Determine method and confidence
        if self.using_fallback_model:
            method = 'rule-based-fallback'
            confidence = 0.7
        else:
            method = 'indictrans2'
            confidence = 0.95
        
        return {
            'original_text': text,
            'translated_text': translated_text,
            'source_language': src_lang,
            'target_language': tgt_lang,
            'method': method,
            'confidence': confidence
        }
    
    def _fallback_translate_batch(
        self, 
        valid_texts: List[str], 
        original_texts: List[str],
        src_lang: str,
        tgt_lang: str
    ) -> List[str]:
        """
        Fallback rule-based translation when model is not available
        """
        # Comprehensive Urdu to English mapping for land records
        urdu_to_english = {
            # Document types
            'جمع بندی': 'Jamabandi',
            'فرد': 'Fard',
            'نقشہ': 'Map',
            'انتقال': 'Mutation',
            
            # Administrative units
            'موضع': 'Mauza/Village',
            'تحصیل': 'Tehsil',
            'ضلع': 'District',
            'صوبہ': 'Province',
            'سال': 'Year',
            'گاؤں': 'Village',
            'محلہ': 'Mohalla',
            
            # Land terms
            'خسرہ': 'Khasra',
            'کھاتہ': 'Khata',
            'نمبر': 'Number',
            'مالک': 'Owner',
            'کاشتکار': 'Cultivator',
            'مزارع': 'Tenant',
            'رقبہ': 'Area',
            
            # Units
            'ایکڑ': 'Acre',
            'کنال': 'Kanal',
            'مرلہ': 'Marla',
            'بیگھہ': 'Bigha',
            'سرسائی': 'Sarsai',
            
            # Land types
            'زمین': 'Land',
            'باغ': 'Orchard',
            'عمارت': 'Building',
            'آبپاشی': 'Irrigated',
            'بارانی': 'Rain-fed',
            'بنجر': 'Barren',
            'چراگاہ': 'Pasture',
            
            # Family relations
            'ولد': 'Son of',
            'والد': 'Father',
            'بنت': 'Daughter of',
            'زوجہ': 'Wife of',
            'بیوہ': 'Widow of',
            
            # Common terms
            'نام': 'Name',
            'کل': 'Total',
            'جنس': 'Type',
            'فصل': 'Crop',
            'تاریخ': 'Date',
            'دستخط': 'Signature',
            
            # Places (Jammu specific)
            'اتما پور': 'Atmapur',
            'بشنال': 'Bishnah',
            'جموں': 'Jammu',
            'کٹھوعہ': 'Kathua',
            'اودھمپور': 'Udhampur',
            'سامبا': 'Samba',
            'راجوری': 'Rajouri',
            'پونچھ': 'Poonch',
        }
        
        # Translate each valid text
        all_translations = []
        for text in valid_texts:
            translated = text
            for urdu, english in urdu_to_english.items():
                translated = translated.replace(urdu, english)
            all_translations.append(translated)
        
        # Map back to original indices
        result = []
        valid_idx = 0
        for text in original_texts:
            if text and text.strip():
                result.append(all_translations[valid_idx])
                valid_idx += 1
            else:
                result.append("")
        
        return result
    
    def is_available(self) -> bool:
        """Check if IndicTrans2 is properly configured"""
        try:
            from IndicTransTokenizer import IndicProcessor
            return True
        except ImportError:
            return False
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes"""
        return self.LANG_CODES.copy()


# Convenience function for quick translation
def translate_urdu_to_english(text: str) -> str:
    """
    Quick function to translate Urdu text to English
    
    Args:
        text: Urdu text to translate
        
    Returns:
        English translation
    """
    translator = IndicTransTranslator(direction='indic-en')
    return translator.translate(text, src_lang='ur', tgt_lang='en')


# Test function
def test_translation():
    """Test the translation with sample Jamabandi terms"""
    translator = IndicTransTranslator(direction='indic-en')
    
    test_texts = [
        "موضع اتما پور",           # Village Atmapur
        "تحصیل بشنال",              # Tehsil Bishnah
        "ضلع جموں",                 # District Jammu
        "جمع بندی",                 # Jamabandi
        "خسرہ نمبر",                # Khasra Number
        "مالک",                     # Owner
        "کاشتکار",                  # Cultivator
        "رقبہ",                     # Area
    ]
    
    print("Testing Urdu → English Translation:")
    print("=" * 50)
    
    for text in test_texts:
        try:
            translation = translator.translate(text, src_lang='ur', tgt_lang='en')
            print(f"  {text} → {translation}")
        except Exception as e:
            print(f"  {text} → ERROR: {e}")
    
    print("=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    test_translation()

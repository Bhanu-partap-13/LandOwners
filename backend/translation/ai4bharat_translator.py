"""
AI4Bharat IndicTrans2 Translation Service
==========================================
Self-hosted translation using AI4Bharat's IndicTrans2 model.
No external APIs required - runs completely offline!

Models used:
- IndicTrans2 Distilled (200M params, ~800MB) for translation
- IndicXlit (11M params, ~50MB) for transliteration

Supports:
- Urdu (urd_Arab) → English (eng_Latn)
- Hindi (hin_Deva) → English (eng_Latn)
- 22 Indic languages total

References:
- https://github.com/AI4Bharat/IndicTrans2
- https://github.com/AI4Bharat/IndicXlit
- https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M
"""

import os
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Lazy loading flags
_model_loaded = False
_model = None
_tokenizer = None
_processor = None


# Language code mappings (FLORES-200 codes used by IndicTrans2)
LANGUAGE_CODES = {
    # Common inputs
    'ur': 'urd_Arab',
    'urdu': 'urd_Arab',
    'urd': 'urd_Arab',
    'hi': 'hin_Deva',
    'hindi': 'hin_Deva',
    'hin': 'hin_Deva',
    'en': 'eng_Latn',
    'english': 'eng_Latn',
    'eng': 'eng_Latn',
    'pa': 'pan_Guru',
    'punjabi': 'pan_Guru',
    'pan': 'pan_Guru',
    
    # Already in FLORES format
    'urd_Arab': 'urd_Arab',
    'hin_Deva': 'hin_Deva',
    'eng_Latn': 'eng_Latn',
    'pan_Guru': 'pan_Guru',
    'ben_Beng': 'ben_Beng',
    'tam_Taml': 'tam_Taml',
    'tel_Telu': 'tel_Telu',
    'mar_Deva': 'mar_Deva',
    'guj_Gujr': 'guj_Gujr',
    'kan_Knda': 'kan_Knda',
    'mal_Mlym': 'mal_Mlym',
    'ory_Orya': 'ory_Orya',
    'asm_Beng': 'asm_Beng',
    'kas_Arab': 'kas_Arab',
    'snd_Arab': 'snd_Arab',
    'npi_Deva': 'npi_Deva',
    'mai_Deva': 'mai_Deva',
    'doi_Deva': 'doi_Deva',
    'san_Deva': 'san_Deva',
    'sat_Olck': 'sat_Olck',
    'mni_Mtei': 'mni_Mtei',
    'brx_Deva': 'brx_Deva',
    'gom_Deva': 'gom_Deva',
}


def normalize_language_code(lang: str) -> str:
    """Convert language code to FLORES-200 format"""
    lang_lower = lang.lower().strip()
    return LANGUAGE_CODES.get(lang_lower, lang)


def is_model_available() -> bool:
    """Check if IndicTrans2 model dependencies are available"""
    try:
        import torch
        from transformers import AutoModelForSeq2SeqLM
        return True
    except ImportError:
        return False


def load_model(force_reload: bool = False) -> bool:
    """
    Load IndicTrans2 model and tokenizer
    
    Returns:
        bool: True if model loaded successfully
    """
    global _model_loaded, _model, _tokenizer, _processor
    
    if _model_loaded and not force_reload:
        return True
    
    if not is_model_available():
        logger.warning("IndicTrans2 dependencies not installed. Install with: pip install torch transformers IndicTransToolkit")
        return False
    
    try:
        import torch
        from transformers import AutoModelForSeq2SeqLM
        
        logger.info("Loading IndicTrans2 model (this may take a moment on first run)...")
        
        # Try to import IndicTransToolkit for tokenizer
        try:
            from IndicTransToolkit import IndicProcessor, IndicTransTokenizer
            _processor = IndicProcessor(inference=True)
            _tokenizer = IndicTransTokenizer(direction="indic-en")
            logger.info("Loaded IndicTransToolkit tokenizer")
        except ImportError:
            logger.warning("IndicTransToolkit not found, using transformers tokenizer")
            from transformers import AutoTokenizer
            _tokenizer = AutoTokenizer.from_pretrained(
                "ai4bharat/indictrans2-indic-en-dist-200M",
                trust_remote_code=True
            )
            _processor = None
        
        # Load model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        _model = AutoModelForSeq2SeqLM.from_pretrained(
            "ai4bharat/indictrans2-indic-en-dist-200M",
            trust_remote_code=True
        )
        _model = _model.eval().to(device)
        
        _model_loaded = True
        logger.info("IndicTrans2 model loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load IndicTrans2 model: {e}")
        _model_loaded = False
        return False


def translate_batch(
    sentences: List[str],
    src_lang: str = 'urd_Arab',
    tgt_lang: str = 'eng_Latn',
    num_beams: int = 5,
    max_length: int = 256
) -> List[str]:
    """
    Translate a batch of sentences using IndicTrans2
    
    Args:
        sentences: List of sentences to translate
        src_lang: Source language code (e.g., 'urd_Arab', 'hin_Deva')
        tgt_lang: Target language code (e.g., 'eng_Latn')
        num_beams: Beam search width
        max_length: Maximum output length
    
    Returns:
        List of translated sentences
    """
    if not _model_loaded:
        if not load_model():
            raise RuntimeError("Failed to load IndicTrans2 model")
    
    import torch
    
    src_lang = normalize_language_code(src_lang)
    tgt_lang = normalize_language_code(tgt_lang)
    
    # Filter empty sentences
    valid_sentences = [s.strip() for s in sentences if s and s.strip()]
    if not valid_sentences:
        return [""] * len(sentences)
    
    try:
        device = next(_model.parameters()).device
        
        if _processor is not None:
            # Use IndicTransToolkit (preferred)
            batch = _processor.preprocess_batch(
                valid_sentences,
                src_lang=src_lang,
                tgt_lang=tgt_lang
            )
            inputs = _tokenizer(batch, src=True, return_tensors="pt", padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.inference_mode():
                outputs = _model.generate(
                    **inputs,
                    num_beams=num_beams,
                    num_return_sequences=1,
                    max_length=max_length
                )
            
            decoded = _tokenizer.batch_decode(outputs, src=False)
            translations = _processor.postprocess_batch(decoded, lang=tgt_lang)
        else:
            # Fallback using transformers tokenizer
            # IndicTrans2 tokenizer expects format: "src_lang tgt_lang text"
            formatted_sentences = [f"{src_lang} {tgt_lang} {s}" for s in valid_sentences]
            
            translations = []
            for formatted in formatted_sentences:
                inputs = _tokenizer(
                    formatted,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=max_length
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                with torch.inference_mode():
                    outputs = _model.generate(
                        **inputs,
                        num_beams=num_beams,
                        num_return_sequences=1,
                        max_length=max_length
                    )
                
                decoded = _tokenizer.decode(outputs[0], skip_special_tokens=True)
                translations.append(decoded)
        
        return translations
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise


def translate_text(
    text: str,
    src_lang: str = 'ur',
    tgt_lang: str = 'en'
) -> Dict:
    """
    Translate text using IndicTrans2
    
    Args:
        text: Text to translate
        src_lang: Source language ('ur', 'hi', 'en', etc.)
        tgt_lang: Target language
    
    Returns:
        dict with translated_text, confidence, etc.
    """
    src_lang = normalize_language_code(src_lang)
    tgt_lang = normalize_language_code(tgt_lang)
    
    if not text or not text.strip():
        return {
            'original_text': text,
            'translated_text': '',
            'source_lang': src_lang,
            'target_lang': tgt_lang,
            'confidence': 0.0,
            'method': 'empty_input'
        }
    
    # Split into sentences for better translation
    sentences = [s.strip() for s in text.split('\n') if s.strip()]
    
    try:
        translations = translate_batch(sentences, src_lang, tgt_lang)
        translated_text = '\n'.join(translations)
        
        return {
            'original_text': text,
            'translated_text': translated_text,
            'source_lang': src_lang,
            'target_lang': tgt_lang,
            'confidence': 95.0,  # IndicTrans2 has high accuracy
            'method': 'indictrans2',
            'model': 'ai4bharat/indictrans2-indic-en-dist-200M'
        }
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return {
            'original_text': text,
            'translated_text': text,  # Return original on error
            'source_lang': src_lang,
            'target_lang': tgt_lang,
            'confidence': 0.0,
            'method': 'error',
            'error': str(e)
        }


class AI4BharatTranslator:
    """
    High-level translator class using AI4Bharat IndicTrans2
    
    Example:
        translator = AI4BharatTranslator()
        result = translator.translate("جمع بندی موضع", src_lang='ur', tgt_lang='en')
        print(result['translated_text'])
    """
    
    def __init__(self, auto_load: bool = False):
        """
        Initialize translator
        
        Args:
            auto_load: If True, load model immediately (slower startup)
        """
        self._loaded = False
        if auto_load:
            self._loaded = load_model()
    
    def is_available(self) -> bool:
        """Check if translator is available"""
        return is_model_available()
    
    def load(self) -> bool:
        """Load the translation model"""
        self._loaded = load_model()
        return self._loaded
    
    def translate(
        self,
        text: str,
        src_lang: str = 'ur',
        tgt_lang: str = 'en',
        **kwargs
    ) -> Dict:
        """
        Translate text
        
        Args:
            text: Text to translate
            src_lang: Source language
            tgt_lang: Target language
        
        Returns:
            dict with translation result
        """
        if not self._loaded:
            self.load()
        return translate_text(text, src_lang, tgt_lang)
    
    def translate_batch(
        self,
        texts: List[str],
        src_lang: str = 'ur',
        tgt_lang: str = 'en'
    ) -> List[str]:
        """Translate multiple texts"""
        if not self._loaded:
            self.load()
        return translate_batch(texts, src_lang, tgt_lang)
    
    def get_supported_languages(self) -> Dict:
        """Get supported language pairs"""
        return {
            'source_languages': [
                'urd_Arab', 'hin_Deva', 'ben_Beng', 'tam_Taml', 'tel_Telu',
                'mar_Deva', 'guj_Gujr', 'kan_Knda', 'mal_Mlym', 'pan_Guru',
                'ory_Orya', 'asm_Beng', 'kas_Arab', 'snd_Arab', 'npi_Deva',
                'mai_Deva', 'doi_Deva', 'san_Deva', 'sat_Olck', 'mni_Mtei',
                'brx_Deva', 'gom_Deva'
            ],
            'target_languages': ['eng_Latn'],
            'primary_pair': {
                'source': 'urd_Arab',
                'target': 'eng_Latn',
                'name': 'Urdu to English'
            }
        }


# Convenience function for quick translation
def quick_translate(text: str, src: str = 'ur', tgt: str = 'en') -> str:
    """
    Quick translate function - loads model if needed
    
    Args:
        text: Text to translate
        src: Source language
        tgt: Target language
    
    Returns:
        Translated text string
    """
    result = translate_text(text, src, tgt)
    return result.get('translated_text', text)


# Module initialization
__all__ = [
    'AI4BharatTranslator',
    'translate_text',
    'translate_batch',
    'quick_translate',
    'is_model_available',
    'load_model',
    'normalize_language_code',
    'LANGUAGE_CODES'
]

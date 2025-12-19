"""
Translation Module - AI4Bharat Powered
======================================
Self-hosted translation using AI4Bharat's IndicTrans2 and IndicXlit.
No external APIs required - runs completely offline!

Available classes:
- AI4BharatTranslator: Main translator using IndicTrans2 (Indic → English)
- IndicXlitTransliterator: Script transliteration using IndicXlit
- SimpleTranslator: Dictionary-based fallback (no dependencies)
- SetuTranslator: Legacy compatibility wrapper

Supported Languages:
- Urdu (urd_Arab) → English
- Hindi (hin_Deva) → English  
- 22 Indic languages total

Usage:
    from translation import AI4BharatTranslator
    
    translator = AI4BharatTranslator()
    result = translator.translate("جمع بندی موضع اتما پور", src_lang='ur')
    print(result['translated_text'])
"""

# AI4Bharat - Primary translators (self-hosted)
try:
    from .ai4bharat_translator import (
        AI4BharatTranslator,
        translate_text as ai4bharat_translate,
        translate_batch,
        quick_translate,
        is_model_available as is_ai4bharat_available
    )
except ImportError:
    AI4BharatTranslator = None
    ai4bharat_translate = None
    translate_batch = None
    quick_translate = None
    is_ai4bharat_available = lambda: False

# IndicXlit - Transliteration
try:
    from .indicxlit_transliterator import (
        IndicXlitTransliterator,
        transliterate_text,
        quick_transliterate,
        is_indicxlit_available
    )
except ImportError:
    IndicXlitTransliterator = None
    transliterate_text = None
    quick_transliterate = None
    is_indicxlit_available = lambda: False

# Legacy/Fallback translators
from .setu_translator import SetuTranslator, RAGTranslator
from .simple_translator import SimpleTranslator, get_translator, translate_urdu_to_english

# Backward compatibility aliases
IndicTransTranslator = SetuTranslator  # Alias for old code
LightweightTranslator = SetuTranslator  # Alias

__all__ = [
    # AI4Bharat (primary)
    'AI4BharatTranslator',
    'ai4bharat_translate',
    'translate_batch',
    'quick_translate',
    'is_ai4bharat_available',
    
    # IndicXlit (transliteration)
    'IndicXlitTransliterator',
    'transliterate_text',
    'quick_transliterate',
    'is_indicxlit_available',
    
    # Legacy/Fallback
    'SimpleTranslator',
    'SetuTranslator',
    'RAGTranslator',
    'get_translator',
    'translate_urdu_to_english',
    
    # Backward compatibility
    'IndicTransTranslator',
    'LightweightTranslator'
]

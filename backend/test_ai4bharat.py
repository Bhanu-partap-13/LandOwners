"""
AI4Bharat Translation Pipeline Test
====================================
Tests the OCR → Translation pipeline with sample Urdu text and PDFs.

Usage:
    python test_ai4bharat.py                    # Basic test
    python test_ai4bharat.py path/to/urdu.pdf   # Test with PDF
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample Urdu text for testing (Jammu land record terms)
SAMPLE_URDU_TEXTS = [
    "جمع بندی موضع اتما پور",         # Revenue record of Atmapur village
    "پٹواری حلقہ",                      # Patwari circle
    "مالکان اراضی",                     # Land owners
    "نمبر کھیوط",                       # Khewat number
    "رقبہ کنال",                        # Area in kanals
    "مربع مرلہ",                        # Square marla
    "موضع چک میاں صاحب سنگھ",          # Village Chak Mian Sahib Singh
    "تحصیل جموں",                       # Tehsil Jammu
    "ضلع جموں",                         # District Jammu
]


def test_simple_translator():
    """Test the dictionary-based translator (no dependencies)"""
    print("\n" + "="*60)
    print("TEST 1: Simple Dictionary Translator")
    print("="*60)
    
    try:
        from translation import SimpleTranslator, translate_urdu_to_english
        
        translator = SimpleTranslator()
        print(f"✓ SimpleTranslator initialized")
        
        for urdu_text in SAMPLE_URDU_TEXTS[:5]:
            result = translator.translate(urdu_text)
            print(f"\n  Input:  {urdu_text}")
            print(f"  Output: {result.get('translated_text', 'N/A')}")
            print(f"  Method: {result.get('translation_type', 'unknown')}")
        
        print("\n✓ Dictionary translator test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Dictionary translator test FAILED: {e}")
        return False


def test_ai4bharat_availability():
    """Check if AI4Bharat dependencies are available"""
    print("\n" + "="*60)
    print("TEST 2: AI4Bharat Dependencies Check")
    print("="*60)
    
    checks = {
        'torch': False,
        'transformers': False,
        'IndicTransToolkit': False,
        'ai4bharat_transliteration': False
    }
    
    # Check PyTorch
    try:
        import torch
        checks['torch'] = True
        device = "CUDA" if torch.cuda.is_available() else "CPU"
        print(f"✓ PyTorch {torch.__version__} ({device})")
    except ImportError:
        print("✗ PyTorch not installed")
    
    # Check Transformers
    try:
        import transformers
        checks['transformers'] = True
        print(f"✓ Transformers {transformers.__version__}")
    except ImportError:
        print("✗ Transformers not installed")
    
    # Check IndicTransToolkit
    try:
        from IndicTransToolkit import IndicProcessor
        checks['IndicTransToolkit'] = True
        print("✓ IndicTransToolkit installed")
    except ImportError:
        print("○ IndicTransToolkit not installed (optional, will use fallback)")
    
    # Check IndicXlit
    try:
        from ai4bharat.transliteration import XlitEngine
        checks['ai4bharat_transliteration'] = True
        print("✓ IndicXlit installed")
    except ImportError:
        print("○ IndicXlit not installed (optional)")
    
    core_available = checks['torch'] and checks['transformers']
    
    if core_available:
        print("\n✓ Core AI4Bharat dependencies available")
    else:
        print("\n✗ Missing core dependencies. Install with:")
        print("  pip install torch transformers")
        print("  pip install git+https://github.com/VarunGumma/IndicTransToolkit.git")
    
    return core_available


def test_ai4bharat_translator():
    """Test the AI4Bharat IndicTrans2 translator"""
    print("\n" + "="*60)
    print("TEST 3: AI4Bharat IndicTrans2 Translation")
    print("="*60)
    
    try:
        from translation import AI4BharatTranslator, is_ai4bharat_available
        
        if not is_ai4bharat_available():
            print("○ AI4Bharat not available, skipping test")
            return None
        
        print("Loading IndicTrans2 model (may take a while on first run)...")
        translator = AI4BharatTranslator(auto_load=False)
        
        # Load model
        if not translator.load():
            print("✗ Failed to load model")
            return False
        
        print("✓ Model loaded successfully")
        
        # Test translations
        for urdu_text in SAMPLE_URDU_TEXTS[:5]:
            result = translator.translate(urdu_text, src_lang='ur', tgt_lang='en')
            print(f"\n  Input:  {urdu_text}")
            print(f"  Output: {result.get('translated_text', 'N/A')}")
            print(f"  Confidence: {result.get('confidence', 0):.1f}%")
        
        print("\n✓ AI4Bharat translator test PASSED")
        return True
        
    except Exception as e:
        logger.exception("AI4Bharat test failed")
        print(f"\n✗ AI4Bharat translator test FAILED: {e}")
        return False


def test_transliteration():
    """Test IndicXlit transliteration"""
    print("\n" + "="*60)
    print("TEST 4: IndicXlit Transliteration")
    print("="*60)
    
    try:
        from translation import IndicXlitTransliterator, is_indicxlit_available
        
        if not is_indicxlit_available():
            print("○ IndicXlit not installed, testing rule-based fallback...")
            from translation.indicxlit_transliterator import rule_based_transliteration
            
            for urdu_text in SAMPLE_URDU_TEXTS[:3]:
                result = rule_based_transliteration(urdu_text, 'ur')
                print(f"\n  Input:  {urdu_text}")
                print(f"  Output: {result.get('transliterated_text', 'N/A')}")
                print(f"  Method: {result.get('method', 'unknown')}")
            
            print("\n○ Rule-based transliteration working (install IndicXlit for better results)")
            return None
        
        xlit = IndicXlitTransliterator()
        
        for urdu_text in SAMPLE_URDU_TEXTS[:3]:
            result = xlit.transliterate(urdu_text, src_lang='ur')
            print(f"\n  Input:  {urdu_text}")
            print(f"  Output: {result.get('transliterated_text', 'N/A')}")
            print(f"  Confidence: {result.get('confidence', 0):.1f}%")
        
        print("\n✓ Transliteration test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Transliteration test FAILED: {e}")
        return False


def test_pdf_processing(pdf_path: str):
    """Test PDF OCR and translation"""
    print("\n" + "="*60)
    print(f"TEST 5: PDF Processing - {os.path.basename(pdf_path)}")
    print("="*60)
    
    if not os.path.exists(pdf_path):
        print(f"✗ PDF not found: {pdf_path}")
        return False
    
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(pdf_path)
        print(f"✓ Opened PDF: {doc.page_count} pages")
        
        # Extract text from first page
        page = doc[0]
        text = page.get_text()
        
        if text.strip():
            print(f"✓ Extracted {len(text)} characters from page 1")
            print(f"\n  First 200 chars:\n  {text[:200]}...")
            
            # Try translation
            from translation import SimpleTranslator
            translator = SimpleTranslator()
            
            # Translate first few lines
            lines = [l.strip() for l in text.split('\n') if l.strip()][:5]
            print(f"\n  Translating {len(lines)} lines...")
            
            for line in lines:
                result = translator.translate(line)
                translated = result.get('translated_text', line)
                if translated != line:
                    print(f"  {line[:50]}... → {translated[:50]}...")
            
            print("\n✓ PDF processing test PASSED")
            return True
        else:
            print("○ No text extracted (may be scanned image PDF)")
            print("  For scanned PDFs, use OCR pipeline")
            return None
        
    except Exception as e:
        print(f"\n✗ PDF processing test FAILED: {e}")
        return False


def print_summary(results: dict):
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ PASSED"
        elif result is False:
            status = "✗ FAILED"
        else:
            status = "○ SKIPPED"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


def main():
    """Run all tests"""
    print("="*60)
    print("AI4BHARAT TRANSLATION PIPELINE TEST")
    print("="*60)
    
    results = {}
    
    # Test 1: Dictionary translator
    results['Dictionary Translator'] = test_simple_translator()
    
    # Test 2: Check dependencies
    ai4bharat_available = test_ai4bharat_availability()
    results['Dependencies Check'] = ai4bharat_available
    
    # Test 3: AI4Bharat translator (if available)
    if ai4bharat_available:
        results['AI4Bharat Translator'] = test_ai4bharat_translator()
    else:
        results['AI4Bharat Translator'] = None
    
    # Test 4: Transliteration
    results['Transliteration'] = test_transliteration()
    
    # Test 5: PDF processing (if path provided)
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        results['PDF Processing'] = test_pdf_processing(pdf_path)
    else:
        # Try default test PDF
        default_pdf = os.path.join(
            os.path.dirname(__file__), 
            '..', 'Documents', 'Original', 'Atmapur.pdf'
        )
        if os.path.exists(default_pdf):
            results['PDF Processing'] = test_pdf_processing(default_pdf)
        else:
            print("\n○ No PDF path provided, skipping PDF test")
            print(f"  Usage: python {sys.argv[0]} path/to/urdu.pdf")
            results['PDF Processing'] = None
    
    # Print summary
    print_summary(results)


if __name__ == '__main__':
    main()

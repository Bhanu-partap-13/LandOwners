"""
OCR Module - Lightweight Cloud-Based Implementation

Uses Bhashini API (Government of India) for OCR and translation.
No heavy dependencies like PyTorch or Tesseract required!

Available classes:
- LightweightOCR: Cloud-based OCR using Bhashini/Google Vision
- LightweightOCRPipeline: Complete OCR+Translation pipeline
- OCRPipeline: Alias for LightweightOCRPipeline (backward compatible)
- MultiLanguageOCR: Alias for LightweightOCR (backward compatible)
"""

# Import lightweight versions by default
from .lightweight_ocr import LightweightOCR, MultiLanguageOCR
from .lightweight_pipeline import LightweightOCRPipeline, OCRPipeline

__all__ = [
    'LightweightOCR',
    'MultiLanguageOCR', 
    'LightweightOCRPipeline',
    'OCRPipeline'
]

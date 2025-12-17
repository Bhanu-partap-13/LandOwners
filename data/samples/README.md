# Sample Test Dataset

This directory contains sample images for testing the OCR system.

## Categories

### 1. English Printed Text
- `english_printed_01.jpg` - Clear, high-quality English land record
- `english_printed_02.jpg` - Slightly faded English document
- `english_printed_03.jpg` - English document with noise

### 2. Hindi Printed Text
- `hindi_printed_01.jpg` - Devanagari script land record
- `hindi_printed_02.jpg` - Hindi document with mixed content
- `hindi_printed_03.jpg` - Low-contrast Hindi document

### 3. Urdu Printed Text
- `urdu_printed_01.jpg` - Clear Urdu Nastaliq script
- `urdu_printed_02.jpg` - Urdu document with Arabic numerals
- `urdu_printed_03.jpg` - Faded Urdu text

### 4. Handwritten Text
- `urdu_handwritten_01.jpg` - Handwritten Urdu notes
- `urdu_handwritten_02.jpg` - Cursive Urdu handwriting
- `english_handwritten_01.jpg` - English cursive handwriting

### 5. Mixed Language
- `mixed_eng_hindi_01.jpg` - English and Hindi mixed
- `mixed_eng_urdu_01.jpg` - English and Urdu mixed
- `mixed_all_languages.jpg` - All three languages

### 6. Challenging Cases
- `skewed_document.jpg` - Skewed/rotated document
- `noisy_document.jpg` - Document with background noise
- `low_resolution.jpg` - Low-resolution scan
- `faded_text.jpg` - Faded/old document
- `multi_column.jpg` - Multi-column layout

## Test Instructions

### Using Python
```python
import os
from backend.utils.ocr_pipeline import OCRPipeline

# Initialize pipeline
pipeline = OCRPipeline()

# Test single image
sample_path = 'data/samples/english_printed_01.jpg'
result = pipeline.process(sample_path)
print(result)

# Test batch processing
sample_dir = 'data/samples'
sample_files = [
    os.path.join(sample_dir, f) 
    for f in os.listdir(sample_dir) 
    if f.endswith(('.jpg', '.png'))
]
results = pipeline.batch_process(sample_files)
```

### Using API
```bash
# Upload and process single image
curl -X POST http://localhost:5000/api/ocr/process-upload \
  -F "file=@data/samples/english_printed_01.jpg" \
  -F 'options={"preprocess": true, "clean_text": true}'

# Batch processing
curl -X POST http://localhost:5000/api/ocr/batch \
  -F "files=@data/samples/english_printed_01.jpg" \
  -F "files=@data/samples/hindi_printed_01.jpg" \
  -F "files=@data/samples/urdu_printed_01.jpg"
```

## Creating Your Own Test Samples

1. **Scan Resolution**: Use at least 300 DPI for best results
2. **Format**: Save as JPG or PNG
3. **Size**: Keep under 16MB (default limit)
4. **Lighting**: Ensure even lighting without shadows
5. **Orientation**: Align documents properly before scanning

## Expected Results

### High Quality (A Grade)
- Clear, high-resolution images
- Proper lighting and contrast
- Straight alignment
- Confidence score: > 0.9

### Good Quality (B Grade)
- Slight fading or noise
- Minor alignment issues
- Confidence score: 0.8 - 0.9

### Fair Quality (C Grade)
- Noticeable noise or degradation
- Some skewing
- Confidence score: 0.7 - 0.8

### Poor Quality (D/F Grade)
- Severe degradation
- Heavy noise or artifacts
- Extreme skewing
- Confidence score: < 0.7

## Notes

- Real test images should be placed in this directory
- The README serves as a template for organizing test data
- Always validate OCR results manually for critical documents
- Use diverse samples to test edge cases

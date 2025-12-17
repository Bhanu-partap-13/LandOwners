# 🌐 Translation Feature Guide

## Overview

The Translation feature provides precise Urdu to English translation for Jamabandi (land record) documents. It integrates OCR processing with Setu-Translate to deliver accurate translations with proper land record terminology.

## Key Features

- **Urdu to English Translation**: Specialized for Jamabandi documents
- **Automatic OCR Integration**: Extracts text from images before translation
- **Land Record Terminology**: Precise translation of technical terms
- **PDF Export**: Download translated documents as formatted PDFs
- **Rule-Based Fallback**: Works even without Setu API access

## Common Jamabandi Terms

| Urdu | Roman Urdu | English |
|------|------------|---------|
| جمع بندی | Jamabandi | Land Revenue Record |
| موضع | Mauza | Village |
| تحصیل | Tehsil | Sub-district |
| ضلع | Zila | District |
| خسرہ | Khasra | Survey Number |
| مالک | Malik | Owner |
| رقبہ | Raqba | Area |
| کشت | Kisht | Cultivation |
| باغ | Bagh | Orchard |

## User Interface

### Upload Section

1. **Drag & Drop**: Drop your Jamabandi document image directly
2. **File Browser**: Click "Choose File" to select from your computer
3. **Supported Formats**: JPG, PNG, PDF (max 16MB)

### Translation Options

- **Translate Document**: Process and display translation
- **Translate & Download PDF**: One-click translation with PDF export
- **Reset**: Clear current results and start over

### Results Display

The results show:
- **Original Urdu Text**: Extracted from the document
- **English Translation**: Precise translation with terminology
- **Translation Metadata**: Confidence score, method, languages
- **Download Button**: Generate and download PDF

## API Endpoints

### 1. Translate Document
```http
POST /api/translate/translate-document
Content-Type: multipart/form-data

file: <image_file>
options: {
  "preprocess": true,
  "clean_text": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original": {
      "raw_text": "جمع بندی...",
      "cleaned_text": "جمع بندی..."
    },
    "translated": {
      "text": "Jamabandi...",
      "confidence": 0.95
    },
    "metadata": {
      "source_language": "ur",
      "target_language": "en",
      "confidence": 0.95,
      "method": "rule-based"
    }
  }
}
```

### 2. Translate Text Only
```http
POST /api/translate/translate-text
Content-Type: application/json

{
  "text": "موضع اتما پور",
  "source_lang": "ur",
  "target_lang": "en"
}
```

### 3. Generate PDF
```http
POST /api/translate/generate-pdf
Content-Type: application/json

{
  "original": {...},
  "translated": {...},
  "metadata": {...}
}
```

**Returns**: PDF file (application/pdf)

### 4. Translate & Download (Combined)
```http
POST /api/translate/translate-and-download
Content-Type: multipart/form-data

file: <image_file>
```

**Returns**: PDF file with complete translation

### 5. Check Translation Status
```http
GET /api/translate/translation-status
```

## Translation Process

```mermaid
graph LR
    A[Upload Image] --> B[OCR Processing]
    B --> C[Text Extraction]
    C --> D[Translation]
    D --> E[PDF Generation]
    E --> F[Download]
```

### Step-by-Step:

1. **Upload**: User uploads Jamabandi document image
2. **Preprocessing**: Image is cleaned and enhanced
3. **OCR**: Text is extracted using Tesseract
4. **Translation**: 
   - Attempts Setu-Translate API
   - Falls back to rule-based translation if needed
5. **Formatting**: Translated text is formatted
6. **PDF Generation**: Creates professional PDF document
7. **Download**: User receives PDF file

## Translation Methods

### 1. Setu-Translate (Primary)
- Uses Setu's neural translation API
- High accuracy for general text
- Requires API key configuration

### 2. Rule-Based (Fallback)
- Dictionary-based translation
- Specialized for land record terms
- Always available
- Fast and reliable

## PDF Output Format

The generated PDF includes:

1. **Header**
   - Document title
   - Generation timestamp

2. **Document Information**
   - Source language
   - Target language
   - Translation confidence
   - Processing method

3. **Original Text Section**
   - Raw Urdu text
   - Cleaned version

4. **Translated Text Section**
   - English translation
   - Formatted for readability

5. **Metadata Table**
   - Processing details
   - Confidence scores
   - System information

6. **Footer**
   - Disclaimer
   - Page numbers

## Configuration

### Backend Setup

1. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Set environment variables (optional):
```bash
export SETU_API_KEY="your_api_key_here"
export SETU_API_URL="https://api.setu.co/translate"
```

3. Start Flask server:
```bash
cd backend
python app.py
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure API URL in `.env`:
```
VITE_API_URL=http://localhost:5000
```

3. Start development server:
```bash
npm run dev
```

## Usage Examples

### Example 1: Basic Translation

**Input Document**: Jamabandi from Atmapur village

**Urdu Text**:
```
جمع بندی
موضع: اتما پور
تحصیل: بشنال
ضلع: جموں
خسرہ نمبر: ۱۲۳
مالک: محمد احمد
```

**English Translation**:
```
Jamabandi
Village: Atmapur
Tehsil: Bishnah
District: Jammu
Khasra Number: 123
Owner: Muhammad Ahmad
```

### Example 2: Using API

```javascript
import translationService from './services/translationService';

// Translate document
const file = document.getElementById('fileInput').files[0];
const result = await translationService.translateDocument(file);
console.log(result.data.translated.text);

// Download PDF
const pdfBlob = await translationService.translateAndDownload(file);
translationService.downloadBlob(pdfBlob, 'jamabandi.pdf');
```

### Example 3: Text-Only Translation

```javascript
const text = "موضع اتما پور";
const result = await translationService.translateText(text, 'ur', 'en');
// Output: { text: "Village Atmapur", confidence: 1.0 }
```

## Troubleshooting

### Issue: Translation Fails

**Solution**:
1. Check file format (JPG, PNG, PDF only)
2. Ensure file size < 16MB
3. Verify backend server is running
4. Check browser console for errors

### Issue: Low Confidence Score

**Reasons**:
- Poor image quality
- Handwritten text
- Unusual terminology

**Solutions**:
- Use higher resolution images
- Ensure good lighting in scans
- Use cleaner document copies

### Issue: PDF Generation Error

**Solution**:
1. Check reportlab is installed: `pip install reportlab`
2. Verify translation data is complete
3. Check disk space for temporary files

### Issue: Incorrect Translation

**Solution**:
- For known terms, update `setu_translator.py` mapping
- Report unknown terms for addition to dictionary
- Consider using higher quality source images

## Performance Tips

1. **Image Quality**: Use 300 DPI scans for best results
2. **File Size**: Compress large images before upload
3. **Batch Processing**: Process multiple documents sequentially
4. **Caching**: Translation results are not cached (by design)

## Security Considerations

1. **File Validation**: Only specific formats allowed
2. **Size Limits**: Maximum 16MB per file
3. **API Keys**: Store in environment variables
4. **CORS**: Configured for localhost development
5. **Input Sanitization**: All text is sanitized before processing

## Future Enhancements

- [ ] Batch translation for multiple documents
- [ ] Language detection (auto-detect source)
- [ ] Translation memory/caching
- [ ] Additional language pairs
- [ ] OCR confidence filtering
- [ ] Interactive PDF with original overlay
- [ ] Export to Word/Excel formats
- [ ] Translation history tracking

## Support

For issues or questions:
1. Check this guide first
2. Review error messages in browser console
3. Check backend logs: `backend/logs/app.log`
4. Verify API connectivity and configuration

## License

Part of J&K AgriStack Land Record OCR System
© 2025

# 🚀 Quick Start: Translation Feature

Get the Urdu-to-English translation feature running in 5 minutes!

## Prerequisites
- Backend and frontend already set up from main OCR system
- reportlab package installed
- react-router-dom package installed

## Installation Steps

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install reportlab==4.0.7
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install react-router-dom@^7.1.3
```

### Step 3: Start Backend

```bash
cd backend
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Registered blueprints: ocr_bp, translation_bp
```

### Step 4: Start Frontend

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v7.2.4  ready in X ms

  ➜  Local:   http://localhost:5173/
```

### Step 5: Access Translation Page

1. Open browser to `http://localhost:5173`
2. Click on **"🌐 Translation"** tab in navigation
3. You're ready to translate!

## First Translation

### Try with Sample Text

1. Create a test image with Urdu text:
   - Text: `جمع بندی موضع اتما پور`
   - Save as PNG/JPG

2. On Translation page:
   - Click "Choose File" or drag & drop
   - Click "Translate Document"
   - View results

3. Expected output:
   ```
   Jamabandi Village Atmapur
   ```

4. Click "Download as PDF" to get formatted document

## Common Jamabandi Terms Supported

| Urdu | English |
|------|---------|
| جمع بندی | Jamabandi |
| موضع | Village |
| تحصیل | Tehsil |
| ضلع | District |
| خسرہ | Khasra |
| مالک | Owner |
| رقبہ | Area |

## Quick Test Commands

### Test Translation API

```bash
# Upload and translate a file
curl -X POST http://localhost:5000/api/translate/translate-document \
  -F "file=@/path/to/jamabandi.jpg" \
  -F 'options={"preprocess": true}' \
  -H "Content-Type: multipart/form-data"
```

### Test Text Translation

```bash
curl -X POST http://localhost:5000/api/translate/translate-text \
  -H "Content-Type: application/json" \
  -d '{"text": "موضع اتما پور", "source_lang": "ur", "target_lang": "en"}'
```

### Check Service Status

```bash
curl http://localhost:5000/api/translate/translation-status
```

Expected response:
```json
{
  "success": true,
  "data": {
    "service": "Translation API",
    "status": "running",
    "translator": "SetuTranslator"
  }
}
```

## Troubleshooting

### Issue: Navigation tab not showing

**Solution:**
```bash
cd frontend
npm install react-router-dom
npm run dev
```

### Issue: PDF download fails

**Solution:**
```bash
cd backend
pip install reportlab
python app.py
```

### Issue: Translation returns empty

**Possible causes:**
1. OCR failed - check image quality
2. No Urdu text detected - verify image contains Urdu
3. Backend error - check console logs

**Debug:**
```bash
# Check backend logs
cd backend
python app.py  # Look for errors in console
```

### Issue: "Module not found: translationService"

**Solution:**
Ensure you created both:
- `frontend/src/services/translationService.js`
- `frontend/src/pages/TranslatePage.jsx`

## Features at a Glance

### ⚡ Quick Actions

- **Translate Document**: Extract + translate + display
- **Translate & Download PDF**: One-click full workflow
- **Download PDF**: Generate PDF from results

### 📄 PDF Contains

- Original Urdu text
- English translation
- Document metadata (confidence, method, timestamp)
- Professional formatting
- Disclaimer footer

### 🎯 Best Results

- Use **300 DPI** scans
- Ensure **good lighting**
- **Clean** document copies
- Supported formats: **JPG, PNG, PDF** (max 16MB)

## Example Usage Flow

1. **Upload** Jamabandi document → 2 seconds
2. **Processing** (OCR + Translation) → 5-10 seconds
3. **View** results on screen → Instant
4. **Download** PDF → 2 seconds

**Total time: ~10-15 seconds per document**

## Next Steps

- Read [TRANSLATION_GUIDE.md](./TRANSLATION_GUIDE.md) for detailed documentation
- Check [README.md](./README.md) for complete system documentation
- Explore API endpoints for programmatic access
- Test with your own Jamabandi documents

## Common Workflows

### Workflow 1: Quick Translation
```
Upload → "Translate & Download PDF" → Done!
```

### Workflow 2: Review First
```
Upload → "Translate Document" → Review → "Download PDF"
```

### Workflow 3: Text Only
```
Use OCR Page → Extract text → Switch to Translation → Translate
```

## Tips for Best Results

1. **Image Quality**: Higher resolution = better accuracy
2. **File Format**: PNG works best, JPG is good, PDF supported
3. **File Size**: Keep under 5MB for faster processing
4. **Document Type**: Works best with Jamabandi forms
5. **Language**: Optimized for Urdu land record terminology

## Support

If you encounter issues:

1. Check this guide
2. Review [TRANSLATION_GUIDE.md](./TRANSLATION_GUIDE.md)
3. Check browser console (F12)
4. Check backend terminal for errors
5. Verify all dependencies installed

## Success Indicators

✅ Backend shows: `Registered blueprints: ocr_bp, translation_bp`
✅ Frontend shows translation tab in navigation
✅ Translation page loads without errors
✅ Can upload and process files
✅ Can download PDFs

## Ready to Use!

The translation feature is now ready. Start translating Jamabandi documents from Urdu to English with professional PDF output!

---

For questions or issues, refer to the main documentation or check the troubleshooting section.

# 📋 Translation Feature - Quick Reference Card

## 🚀 Quick Start
```bash
# Backend
cd backend && pip install reportlab && python app.py

# Frontend (new terminal)
cd frontend && npm install react-router-dom && npm run dev

# Access: http://localhost:5173 → Click "🌐 Translation"
```

## 🎯 Three-Click Workflow
1. **Upload** Jamabandi image (drag & drop or click)
2. **Click** "Translate & Download PDF" button
3. **Done!** PDF downloaded automatically

## 📡 API Quick Reference

### Translate Document (with OCR)
```bash
curl -X POST http://localhost:5000/api/translate/translate-document \
  -F "file=@jamabandi.jpg" \
  -F 'options={"preprocess": true}'
```

### Translate Text Only
```bash
curl -X POST http://localhost:5000/api/translate/translate-text \
  -H "Content-Type: application/json" \
  -d '{"text": "موضع اتما پور", "source_lang": "ur", "target_lang": "en"}'
```

### Download PDF (One Request)
```bash
curl -X POST http://localhost:5000/api/translate/translate-and-download \
  -F "file=@jamabandi.jpg" \
  --output translation.pdf
```

## 🔤 Essential Terms Cheat Sheet

| Urdu | English | Use Case |
|------|---------|----------|
| جمع بندی | Jamabandi | Document title |
| موضع | Village | Location |
| تحصیل | Tehsil | Administrative unit |
| ضلع | District | Region |
| خسرہ | Khasra | Survey/plot number |
| مالک | Owner | Land owner |
| رقبہ | Area | Land area |

### Sample Document Translation

**Input (Urdu):**
```
جمع بندی
موضع: اتما پور
تحصیل: بشنال
ضلع: جموں
```

**Output (English):**
```
Jamabandi
Village: Atmapur
Tehsil: Bishnah
District: Jammu
```

## 🖥️ UI Navigation

### Page Structure
```
Header: "Land Record OCR & Translation System"
  ↓
Tabs: [📄 OCR Processing] [🌐 Translation] ← Click here
  ↓
Upload Section | Results Section
```

### Buttons Explained
- **Translate Document**: Show results on screen
- **Translate & Download PDF**: Direct PDF download
- **Download as PDF**: Generate PDF from current results
- **Reset**: Clear and start over

## 📂 File Requirements

| Property | Requirement |
|----------|-------------|
| Format | JPG, PNG, PDF |
| Max Size | 16 MB |
| Resolution | 300 DPI recommended |
| Language | Urdu text required |

## ⚙️ Configuration Files

### Backend `.env`
```env
FLASK_ENV=development
TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe
SETU_API_KEY=optional_for_enhanced_translation
```

### Frontend `.env`
```env
VITE_API_URL=http://localhost:5000
```

## 🔧 Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Translation tab missing | `npm install react-router-dom` |
| PDF fails | `pip install reportlab` |
| CORS error | Check backend is on port 5000 |
| File upload fails | Check file size < 16MB |
| Empty translation | Verify image contains Urdu text |

## 📊 Performance Benchmarks

| Task | Average Time |
|------|--------------|
| Upload | 2 seconds |
| OCR + Translate | 5-10 seconds |
| PDF Generation | 2 seconds |
| **Total** | **10-15 seconds** |

## 🎨 PDF Output Includes

✅ Document header with title
✅ Original Urdu text (cleaned)
✅ English translation
✅ Confidence scores
✅ Processing metadata
✅ Timestamp
✅ Professional formatting

## 🔐 Security Notes

- File validation on upload
- Size limits enforced (16MB)
- Text sanitization automatic
- No data stored permanently
- CORS configured for localhost

## 📖 Documentation Links

- **Full Guide**: [TRANSLATION_GUIDE.md](./TRANSLATION_GUIDE.md)
- **Quick Start**: [TRANSLATION_QUICKSTART.md](./TRANSLATION_QUICKSTART.md)
- **Implementation**: [TRANSLATION_IMPLEMENTATION.md](./TRANSLATION_IMPLEMENTATION.md)
- **Main README**: [README.md](./README.md)

## 🧪 Test Commands

### Check Backend Status
```bash
curl http://localhost:5000/api/translate/translation-status
```

### Test Frontend Routes
- OCR: `http://localhost:5173/`
- Translation: `http://localhost:5173/translate`

## 💡 Pro Tips

1. **Best Image Quality**: Use 300 DPI scans
2. **Faster Processing**: Keep files under 5MB
3. **Better Accuracy**: Ensure good contrast
4. **Quick Workflow**: Use "Translate & Download PDF"
5. **Multiple Docs**: Process one at a time for now

## 📞 Support Checklist

Before asking for help:
- [ ] Backend running on port 5000?
- [ ] Frontend running on port 5173?
- [ ] All dependencies installed?
- [ ] File format correct (JPG/PNG/PDF)?
- [ ] File size under 16MB?
- [ ] Checked browser console (F12)?
- [ ] Checked backend terminal for errors?

## 🎯 Success Indicators

✅ See "🌐 Translation" tab in navigation
✅ Can upload files via drag & drop
✅ Progress bar shows during processing
✅ Results display with original + translated text
✅ PDF downloads successfully
✅ No errors in browser console

## 🚦 Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Translation complete |
| 400 | Bad Request - Check file/parameters |
| 415 | Unsupported format - Use JPG/PNG/PDF |
| 500 | Server Error - Check backend logs |

## 📝 Common Use Cases

### Use Case 1: Quick Translation
```
Upload → "Translate & Download PDF" → Done
Time: ~12 seconds
```

### Use Case 2: Review Before Download
```
Upload → "Translate Document" → Review → "Download PDF"
Time: ~15 seconds
```

### Use Case 3: API Integration
```javascript
const file = document.getElementById('input').files[0];
const pdf = await translationService.translateAndDownload(file);
translationService.downloadBlob(pdf, 'output.pdf');
```

## 🔄 Complete Workflow Diagram

```
┌──────────────┐
│ Select File  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Upload Image │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  OCR + Clean │ ← Automatic
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Translate   │ ← Rule-based
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Generate PDF │ ← Professional format
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Download   │ ← One file
└──────────────┘
```

## 📦 Dependencies Summary

### Backend
- Flask 3.0.0
- reportlab 4.0.7
- Tesseract OCR
- OpenCV

### Frontend
- React 19.2.0
- react-router-dom 7.1.3
- Vite 7.2.4
- Tailwind CSS 4.1.18
- axios 1.13.2

---

**Keep this card handy for quick reference!**

For detailed information, see the full documentation files.

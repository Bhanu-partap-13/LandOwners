# 🚀 Lightweight OCR Setup Guide

This guide explains how to set up the **lightweight** version of the Land Record OCR system that uses **cloud APIs** instead of heavy local models.

## 📊 Comparison: Old vs New

| Aspect | Old (Heavy) | New (Lightweight) |
|--------|-------------|-------------------|
| **Package Size** | ~2GB | ~50MB |
| **Dependencies** | PyTorch, Transformers, Tesseract | Just requests + PIL |
| **Setup Time** | 30+ minutes | 5 minutes |
| **GPU Required** | Optional but recommended | Not needed |
| **Cost** | Free (but heavy) | Free (Bhashini API) |
| **Accuracy** | Good | Excellent (Bhashini/Google) |

## 🔧 Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

That's it! No Tesseract installation, no model downloads.

### Step 2: Get Bhashini API Credentials (FREE)

1. **Register** at [https://bhashini.gov.in/ulca/user/register](https://bhashini.gov.in/ulca/user/register)
2. **Verify** your email
3. **Login** at [https://bhashini.gov.in/ulca/user/login](https://bhashini.gov.in/ulca/user/login)
4. Go to **My Profile** section
5. Click **Generate** to create an API key
6. Copy your **User ID** and **API Key**

### Step 3: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your credentials
BHASHINI_USER_ID=your_user_id_here
BHASHINI_API_KEY=your_api_key_here
```

### Step 4: Run the Server

```bash
python -m flask run
# or
python app.py
```

## 🌐 API Endpoints

### Health Check
```
GET /api/health
```
Returns:
```json
{
  "status": "healthy",
  "mode": "lightweight",
  "bhashini_configured": true,
  "backends_available": ["bhashini"]
}
```

### Upload & Process
```
POST /api/ocr/process-upload
Content-Type: multipart/form-data

file: <your_image_or_pdf>
```

### Process Existing File
```
POST /api/ocr/process
Content-Type: application/json

{
  "filepath": "/path/to/file.pdf",
  "options": {
    "translate": true,
    "source_lang": "ur",
    "target_lang": "en"
  }
}
```

## 📋 Supported Languages

| Code | Language | OCR | Translation |
|------|----------|-----|-------------|
| `ur` | Urdu | ✅ | ✅ |
| `hi` | Hindi | ✅ | ✅ |
| `en` | English | ✅ | ✅ |
| `pa` | Punjabi | ✅ | ✅ |
| `bn` | Bengali | ✅ | ✅ |
| `ta` | Tamil | ✅ | ✅ |
| `te` | Telugu | ✅ | ✅ |
| `mr` | Marathi | ✅ | ✅ |
| `gu` | Gujarati | ✅ | ✅ |
| +13 more | Indian Languages | ✅ | ✅ |

## 🔄 Fallback Options

### Option 1: Google Cloud Vision (Recommended Fallback)
- **Free Tier**: 1,000 requests/month
- **Setup**: [console.cloud.google.com](https://console.cloud.google.com)

```bash
# Add to .env
GOOGLE_CLOUD_API_KEY=your_google_api_key
```

### Option 2: Local Tesseract (Legacy)
If you need offline capability:

```bash
# Install Tesseract
# Windows: choco install tesseract
# Linux: sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-urd

# Add to requirements
pip install pytesseract

# Set mode in .env
OCR_MODE=local
```

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React)                       │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                Flask Backend (Lightweight)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Routes     │  │   Pipeline   │  │   Services   │   │
│  │  (API)       │→ │  (OCR+Trans) │→ │  (Bhashini)  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTPS API
                         ▼
┌──────────────────────────────────────────────────────────┐
│              Bhashini API (Gov of India)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │     OCR      │  │  Translation │  │     TTS      │   │
│  │  (22 langs)  │  │  (NMT AI4B)  │  │  (Optional)  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────────────────────────────────────────┘
```

## 🔒 Security Notes

1. **Never commit** your `.env` file
2. Bhashini API keys are **free but rate-limited**
3. For production, use **environment variables** not files

## 📞 Support

- **Bhashini Support**: ceo-dibd@digitalgov.co.in
- **API Docs**: [bhashini.gitbook.io/bhashini-apis](https://bhashini.gitbook.io/bhashini-apis)

## 🎉 Benefits of Lightweight Mode

1. ✅ **No GPU needed** - Works on any computer
2. ✅ **Fast setup** - 5 minutes vs 30+ minutes
3. ✅ **Small footprint** - 50MB vs 2GB
4. ✅ **Better accuracy** - Government AI models
5. ✅ **Always updated** - Cloud models improve automatically
6. ✅ **Free forever** - Government initiative

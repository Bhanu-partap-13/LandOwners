# 🏠 LandOwners - Complete Setup & Reference Guide

A comprehensive web application for digitizing and translating Urdu/Hindi land records (Jamabandi) from Jammu & Kashmir. Uses AI-powered OCR and neural machine translation to convert scanned land documents into searchable, English-translated digital records.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Node](https://img.shields.io/badge/node-18+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Complete Project Structure](#complete-project-structure)
5. [Installation Guide](#installation-guide)
   - [Step 1: Clone Repository](#step-1-clone-repository)
   - [Step 2: Backend Setup](#step-2-backend-setup)
   - [Step 3: Frontend Setup](#step-3-frontend-setup)
   - [Step 4: Tesseract OCR Setup](#step-4-tesseract-ocr-setup)
   - [Step 5: HuggingFace Setup](#step-5-huggingface-setup)
   - [Step 6: IndicTrans Setup](#step-6-indictrans-setup)
6. [Running the Application](#running-the-application)
7. [API Endpoints](#api-endpoints)
8. [File Roles & Descriptions](#file-roles--descriptions)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)
11. [All Commands Reference](#all-commands-reference)

---

## 🎯 Overview

LandOwners is designed to:
- **OCR**: Extract text from scanned Jamabandi (land record) documents
- **Translate**: Convert Urdu/Hindi text to English using AI4Bharat's IndicTrans2
- **RAG Processing**: Handle large PDFs (200+ pages) efficiently using chunking and caching
- **Search**: Semantic search across processed documents
- **Export**: Generate translated PDF reports

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 7, Tailwind CSS 4 |
| Backend | Flask 3.0, Python 3.11+ |
| OCR | Tesseract OCR, PyTesseract |
| Translation | IndicTrans2 (AI4Bharat), HuggingFace Transformers |
| ML Framework | PyTorch 2.1 |
| PDF Processing | PyMuPDF, pdf2image, Poppler |

---

## ✨ Features

- 📄 **Multi-format Support**: PDF, JPG, PNG, TIFF
- 🌐 **Multi-language OCR**: Urdu, Hindi, English
- 🤖 **Neural Machine Translation**: IndicTrans2 model (200M parameters)
- ⚡ **RAG Processing**: Stream large documents page-by-page
- 🔍 **Semantic Search**: Find relevant sections using vector embeddings
- 💾 **Translation Caching**: 5000x+ speedup for repeated terms
- 📊 **Progress Tracking**: Real-time processing status
- 📑 **PDF Export**: Generate translated document reports

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux, macOS
- **RAM**: 8 GB (16 GB recommended for large PDFs)
- **Storage**: 5 GB free space (for models)
- **Python**: 3.11 or higher
- **Node.js**: 18 or higher

### Required Software
| Software | Version | Purpose |
|----------|---------|---------|
| Git | Latest | Version control |
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| Tesseract OCR | 5.0+ | Text extraction |
| Poppler | Latest | PDF to image conversion |

---

## 📁 Complete Project Structure

```
C:\Jammu\LandOwners\
│
├── 📂 backend/                          # Flask API Server (Python)
│   │
│   ├── 📄 app.py                        # Main Flask app entry point
│   ├── 📄 config.py                     # Configuration & environment settings
│   ├── 📄 requirements.txt              # Python package dependencies
│   ├── 📄 Dockerfile                    # Docker container config
│   ├── 📄 .env.example                  # Environment template
│   │
│   ├── 📂 routes/                       # API Route Handlers
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ocr_routes.py             # /api/ocr/* endpoints
│   │   ├── 📄 translation_routes.py     # /api/translate/* endpoints
│   │   └── 📄 rag_routes.py             # /api/rag/* endpoints (large PDFs)
│   │
│   ├── 📂 utils/                        # Core Processing Modules
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ocr_engine.py             # Tesseract OCR wrapper
│   │   ├── 📄 ocr_pipeline.py           # Full OCR pipeline orchestrator
│   │   ├── 📄 indictrans_translator.py  # IndicTrans2 model wrapper
│   │   ├── 📄 setu_translator.py        # High-level translation API
│   │   ├── 📄 rag_document_processor.py # RAG for large documents
│   │   ├── 📄 image_processing.py       # Image preprocessing
│   │   ├── 📄 language_detector.py      # Detect Urdu/Hindi/English
│   │   ├── 📄 text_cleaner.py           # Clean OCR output
│   │   ├── 📄 transliterator.py         # Script conversion
│   │   ├── 📄 upload_handler.py         # File upload management
│   │   ├── 📄 pdf_generator.py          # Generate PDF reports
│   │   ├── 📄 response_formatter.py     # API response formatting
│   │   ├── 📄 confidence_scorer.py      # OCR confidence scoring
│   │   ├── 📄 urdu_ocr.py               # Urdu-specific OCR
│   │   └── 📄 performance.py            # Performance monitoring
│   │
│   ├── 📂 uploads/                      # Uploaded files storage
│   ├── 📂 cache/                        # Translation & RAG cache
│   │   └── 📂 rag/                      # RAG document cache
│   ├── 📂 models/                       # ML model storage
│   ├── 📂 logs/                         # Application logs
│   ├── 📂 temp/                         # Temporary files
│   ├── 📂 tests/                        # Backend unit tests
│   │
│   ├── 📄 test_translation.py           # Translation test script
│   ├── 📄 test_rag_processor.py         # RAG processor test
│   ├── 📄 SETU_INTEGRATION.md           # Setu integration docs
│   └── 📄 BACKEND_FIXES.md              # Backend fixes documentation
│
├── 📂 frontend/                         # React Frontend (JavaScript)
│   │
│   ├── 📄 package.json                  # Node.js dependencies
│   ├── 📄 package-lock.json             # Dependency lock file
│   ├── 📄 vite.config.js                # Vite build configuration
│   ├── 📄 tailwind.config.js            # Tailwind CSS config
│   ├── 📄 postcss.config.js             # PostCSS configuration
│   ├── 📄 eslint.config.js              # ESLint code style
│   ├── 📄 vitest.config.js              # Test configuration
│   ├── 📄 index.html                    # HTML entry point
│   ├── 📄 Dockerfile                    # Docker container config
│   ├── 📄 nginx.conf                    # Nginx config (production)
│   ├── 📄 .env.example                  # Environment template
│   │
│   ├── 📂 src/                          # Source Code
│   │   ├── 📄 main.jsx                  # React entry point
│   │   ├── 📄 App.jsx                   # Main App + Router
│   │   ├── 📄 App.css                   # Global styles
│   │   ├── 📄 index.css                 # Tailwind imports
│   │   │
│   │   ├── 📂 components/               # Reusable UI Components
│   │   │   ├── 📄 Dashboard.jsx         # Main dashboard view
│   │   │   ├── 📄 ImageUpload.jsx       # File upload component
│   │   │   ├── 📄 ProcessingStatus.jsx  # Progress indicator
│   │   │   ├── 📄 ResultsDisplay.jsx    # OCR results display
│   │   │   ├── 📄 ComparisonView.jsx    # Original vs Translated
│   │   │   └── 📄 ErrorBoundary.jsx     # Error handling
│   │   │
│   │   ├── 📂 pages/                    # Page Components
│   │   │   └── 📄 TranslatePage.jsx     # Translation page
│   │   │
│   │   ├── 📂 services/                 # API Service Layer
│   │   ├── 📂 hooks/                    # Custom React Hooks
│   │   ├── 📂 utils/                    # Utility Functions
│   │   └── 📂 assets/                   # Static Assets
│   │
│   ├── 📂 public/                       # Public static files
│   ├── 📂 tests/                        # Frontend tests
│   └── 📂 node_modules/                 # Node packages (auto-generated)
│
├── 📂 data/                             # Sample data & documents
│
├── 📄 docker-compose.yml                # Docker multi-container setup
├── 📄 setup.bat                         # Windows setup script
├── 📄 setup.sh                          # Linux/Mac setup script
├── 📄 deploy.bat                        # Windows deployment
├── 📄 deploy.sh                         # Linux/Mac deployment
│
├── 📄 README.md                         # Project overview
├── 📄 SETUP_GUIDE.md                    # This detailed guide
├── 📄 LICENSE                           # MIT License
├── 📄 CONTRIBUTING.md                   # Contribution guidelines
├── 📄 CHANGELOG.md                      # Version history
├── 📄 QUICKSTART.md                     # Quick start guide
├── 📄 TRANSLATION_GUIDE.md              # Translation feature docs
├── 📄 TRANSLATION_IMPLEMENTATION.md     # Implementation details
├── 📄 TRANSLATION_QUICKSTART.md         # Quick translation setup
├── 📄 TRANSLATION_REFERENCE.md          # Translation reference
├── 📄 INTEGRATION_TESTING.md            # Testing documentation
└── 📄 PROJECT_SUMMARY.md                # Project summary
```

---

## 🚀 Installation Guide

### Step 1: Clone Repository

```bash
# Navigate to your workspace
cd C:\Jammu

# Clone repository (if not already done)
git clone https://github.com/yourusername/LandOwners.git

# Enter project directory
cd LandOwners
```

---

### Step 2: Backend Setup

#### 2.1 Create Python Virtual Environment

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Windows CMD)
.\venv\Scripts\activate.bat

# Activate virtual environment (Linux/Mac)
source venv/bin/activate
```

**You should see `(venv)` in your terminal prompt.**

#### 2.2 Upgrade pip

```bash
python -m pip install --upgrade pip
```

#### 2.3 Install Core Requirements

```bash
pip install -r requirements.txt
```

#### 2.4 Install Additional Packages

```bash
# PDF Processing
pip install pymupdf

# Tokenization & NLP
pip install sentencepiece
pip install sacremoses
pip install indic-nlp-library

# HuggingFace Hub
pip install huggingface_hub

# NLTK Data
python -c "import nltk; nltk.download('punkt')"
```

#### 2.5 Install IndicTransTokenizer

```bash
# Option 1: From local IndicLLMSuite (recommended)
cd C:\Jammu\IndicLLMSuite\IndicTransTokenizer
pip install -e .
cd C:\Jammu\LandOwners\backend

# Option 2: From GitHub
pip install git+https://github.com/AI4Bharat/IndicLLMSuite.git#subdirectory=IndicTransTokenizer
```

#### 2.6 Create Environment File

```powershell
# Copy template
copy .env.example .env

# Edit the file
notepad .env
```

**Edit `.env` with these values:**

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-random-secret-key-here

# Paths
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler\Library\bin

# Upload Settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800

# HuggingFace Token (get from Step 5)
HF_TOKEN=hf_your_token_here

# CORS Origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

### Step 3: Frontend Setup

#### 3.1 Navigate to Frontend

```bash
cd C:\Jammu\LandOwners\frontend
```

#### 3.2 Install Node Dependencies

```bash
# Install all packages
npm install

# If you see peer dependency warnings, use:
npm install --legacy-peer-deps
```

#### 3.3 Create Environment File

```powershell
# Copy template
copy .env.example .env

# Edit file
notepad .env
```

**Edit `.env`:**

```env
VITE_API_URL=http://localhost:5000/api
```

---

### Step 4: Tesseract OCR Setup

#### Windows Installation

1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Run Installer:**
   - Choose installation path (default: `C:\Program Files\Tesseract-OCR`)
   - **IMPORTANT:** Select additional languages during install:
     - ✅ Hindi (hin)
     - ✅ Urdu (urd)
     - ✅ English (eng) - included by default

3. **Add to PATH:**
   - Open System Properties → Environment Variables
   - Add to PATH: `C:\Program Files\Tesseract-OCR`
   - Or set in `.env` file

4. **Verify Installation:**
   ```bash
   tesseract --version
   tesseract --list-langs
   ```

   Expected output:
   ```
   tesseract 5.3.3
   ...
   List of available languages (3):
   eng
   hin
   urd
   ```

#### Linux Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-hin tesseract-ocr-urd

# Fedora
sudo dnf install tesseract tesseract-langpack-hin tesseract-langpack-urd

# Verify
tesseract --version
tesseract --list-langs
```

#### macOS Installation

```bash
# Using Homebrew
brew install tesseract
brew install tesseract-lang

# Verify
tesseract --version
tesseract --list-langs
```

---

### Step 5: HuggingFace Setup

The IndicTrans2 translation model requires HuggingFace authentication.

#### 5.1 Create HuggingFace Account

1. Go to: https://huggingface.co/join
2. Create a free account
3. Verify your email address

#### 5.2 Accept IndicTrans2 License

1. Go to: https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M
2. Click **"Agree and access repository"**
3. Read and accept the license terms
4. You should see "You have access to this model"

#### 5.3 Create Access Token

1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Configure token:
   - **Name:** `LandOwners`
   - **Type:** `Read`
4. Click **"Generate"**
5. **Copy the token** (starts with `hf_`)
6. **Save it somewhere safe** - you can't see it again!

#### 5.4 Login to HuggingFace CLI

```bash
# Method 1: Interactive login (paste token when prompted)
huggingface-cli login

# Method 2: Direct login with token
python -m huggingface_hub.commands.huggingface_cli login --token hf_YOUR_TOKEN_HERE

# Verify login
huggingface-cli whoami
```

Expected output:
```
Your username: yourusername
```

#### 5.5 Set Token in Environment

Add to your `backend/.env` file:
```env
HF_TOKEN=hf_YOUR_TOKEN_HERE
```

---

### Step 6: IndicTrans Setup

#### 6.1 Automatic Model Download

The model (~913 MB) downloads automatically on first use:

```bash
cd C:\Jammu\LandOwners\backend
python test_translation.py
```

You'll see:
```
Loading IndicTrans2 model... (this may take a moment)
Downloading model.safetensors: 100%|████| 913M/913M
IndicTrans2 model loaded successfully on cpu
```

#### 6.2 Fix Tokenizer Files (If Needed)

If you see error: `No such file or directory: 'dict.SRC.json'`

```powershell
# Find IndicTransTokenizer installation
python -c "import IndicTransTokenizer; print(IndicTransTokenizer.__file__)"

# Example output: C:\Users\User\...\site-packages\IndicTransTokenizer\__init__.py

# Copy dictionary files
# From: C:\Jammu\IndicLLMSuite\IndicTransTokenizer\IndicTransTokenizer\
# To:   [site-packages location]\IndicTransTokenizer\

xcopy "C:\Jammu\IndicLLMSuite\IndicTransTokenizer\IndicTransTokenizer\indic-en" "C:\Users\YourUser\AppData\Local\Programs\Python\Python311\Lib\site-packages\IndicTransTokenizer\indic-en\" /E /I /Y

xcopy "C:\Jammu\IndicLLMSuite\IndicTransTokenizer\IndicTransTokenizer\en-indic" "C:\Users\YourUser\AppData\Local\Programs\Python\Python311\Lib\site-packages\IndicTransTokenizer\en-indic\" /E /I /Y
```

#### 6.3 Test Translation

```bash
cd C:\Jammu\LandOwners\backend
python test_translation.py
```

Expected output:
```
============================================================
SETU-TRANSLATE INTEGRATION TEST
============================================================
Testing IndicTransTranslator
--------------------------------------------------
  موضع اتما پور        → Moza Itmapur
  تحصیل بشنال          → Tehsil Bishnal
  ضلع جموں             → Jammu district
  مالک                 → The owner's
============================================================
ALL TESTS COMPLETED!
```

---

## ▶️ Running the Application

### Start Backend Server

```powershell
# Terminal 1: Backend
cd C:\Jammu\LandOwners\backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Flask server
python app.py
```

**Backend runs at: http://localhost:5000**

You should see:
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### Start Frontend Server

```powershell
# Terminal 2: Frontend
cd C:\Jammu\LandOwners\frontend

# Start Vite dev server
npm run dev
```

**Frontend runs at: http://localhost:5173**

You should see:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

### Access the Application

Open your browser and go to: **http://localhost:5173**

---

## 🔌 API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/api/health` | Health check status |

### OCR Endpoints (`/api/ocr`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ocr/upload` | Upload image/PDF file |
| POST | `/api/ocr/process` | Process file through OCR |
| GET | `/api/ocr/result/{id}` | Get OCR results |

### Translation Endpoints (`/api/translate`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/translate/text` | Translate text (Urdu → English) |
| POST | `/api/translate/document` | Translate full document |
| POST | `/api/translate/structured` | Translate structured land record |

### RAG Endpoints (`/api/rag`) - For Large PDFs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rag/process` | Process PDF (batch mode) |
| POST | `/api/rag/process/stream` | Process PDF (streaming - SSE) |
| GET | `/api/rag/progress` | Get processing progress |
| POST | `/api/rag/search` | Semantic search in processed docs |
| POST | `/api/rag/translate/query` | RAG-style translation lookup |
| POST | `/api/rag/cache/clear` | Clear processing cache |
| POST | `/api/rag/estimate` | Estimate processing time |
| POST | `/api/rag/upload-and-process` | Upload + process in one call |

---

## 📂 File Roles & Descriptions

### Backend Core Files

| File | Purpose |
|------|---------|
| `app.py` | Flask application factory, initializes app, registers blueprints, sets up CORS |
| `config.py` | Configuration classes for dev/prod/test environments, loads `.env` settings |
| `requirements.txt` | Python package dependencies with versions |

### Backend Routes

| File | Purpose |
|------|---------|
| `routes/ocr_routes.py` | Handles `/api/ocr/*` - file upload, OCR processing, results retrieval |
| `routes/translation_routes.py` | Handles `/api/translate/*` - text and document translation |
| `routes/rag_routes.py` | Handles `/api/rag/*` - large PDF streaming, search, caching |

### Backend Utils (Core Processing)

| File | Purpose |
|------|---------|
| `utils/ocr_engine.py` | Tesseract wrapper - `TesseractOCR` class for text extraction |
| `utils/ocr_pipeline.py` | Orchestrates full pipeline: preprocess → OCR → clean → translate |
| `utils/indictrans_translator.py` | IndicTrans2 model wrapper - loads model, handles batch translation |
| `utils/setu_translator.py` | High-level translation API with fallback to rule-based translation |
| `utils/rag_document_processor.py` | RAG processor - chunking, caching, vector search for 200+ page PDFs |
| `utils/image_processing.py` | Image preprocessing - denoise, deskew, contrast enhancement |
| `utils/language_detector.py` | Detects script/language (Urdu, Hindi, English) in text |
| `utils/text_cleaner.py` | Cleans OCR artifacts, fixes common errors, normalizes text |
| `utils/transliterator.py` | Converts between scripts (Urdu ↔ Roman ↔ Devanagari) |
| `utils/upload_handler.py` | File upload validation, storage, PDF extraction |
| `utils/pdf_generator.py` | Generates translated PDF documents using ReportLab |
| `utils/response_formatter.py` | Standardizes API JSON responses |
| `utils/confidence_scorer.py` | Calculates OCR confidence scores |
| `utils/urdu_ocr.py` | Urdu-specific OCR handling |

### Frontend Core Files

| File | Purpose |
|------|---------|
| `main.jsx` | React entry point - renders App to DOM |
| `App.jsx` | Main app component - routing setup, layout |
| `App.css` | Global CSS styles |
| `index.css` | Tailwind CSS imports |

### Frontend Components

| File | Purpose |
|------|---------|
| `components/Dashboard.jsx` | Main dashboard - upload + results view |
| `components/ImageUpload.jsx` | Drag-drop file upload with preview |
| `components/ProcessingStatus.jsx` | Progress bar, status messages during processing |
| `components/ResultsDisplay.jsx` | Shows OCR extracted text, confidence scores |
| `components/ComparisonView.jsx` | Side-by-side original image vs translated text |
| `components/ErrorBoundary.jsx` | React error boundary for graceful error handling |
| `pages/TranslatePage.jsx` | Dedicated translation page UI |

### Frontend Services & Utils

| File | Purpose |
|------|---------|
| `services/api.js` | Axios HTTP client configured for backend API |
| `hooks/*.js` | Custom React hooks for state management |
| `utils/*.js` | Helper functions for formatting, validation |

---

## ⚙️ Configuration

### Backend Configuration (`backend/config.py`)

```python
class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    
    # Tesseract
    TESSERACT_PATH = os.environ.get('TESSERACT_PATH', 
        'C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
    
    # Poppler
    POPPLER_PATH = os.environ.get('POPPLER_PATH', 
        'C:\\poppler\\Library\\bin')
    
    # Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
```

### Frontend Configuration (`frontend/vite.config.js`)

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

---

## 🔧 Troubleshooting

### Issue: "tesseract is not installed or not in PATH"

**Solution:**
```bash
# Check if installed
tesseract --version

# If not found, set full path in .env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Issue: "No module named 'IndicTransTokenizer'"

**Solution:**
```bash
cd C:\Jammu\IndicLLMSuite\IndicTransTokenizer
pip install -e .
```

### Issue: "dict.SRC.json not found"

**Solution:**
```powershell
# Copy tokenizer dictionary files
xcopy "C:\Jammu\IndicLLMSuite\IndicTransTokenizer\IndicTransTokenizer\indic-en" "[site-packages]\IndicTransTokenizer\indic-en\" /E /I /Y
```

### Issue: "Access to model denied" or "gated repo"

**Solution:**
1. Accept license at: https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M
2. Login: `huggingface-cli login`
3. Verify: `huggingface-cli whoami`

### Issue: "No module named 'keras.src.engine'"

**Solution:** This is handled automatically by the code patching UrduNormalizer. No action needed.

### Issue: Frontend CORS errors

**Solution:**
Ensure backend has CORS configured:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Issue: PDF processing fails

**Solution:**
```bash
# Install poppler
# Windows: https://github.com/oschwartz10612/poppler-windows/releases
# Extract to C:\poppler
# Add to PATH: C:\poppler\Library\bin
```

### Issue: npm install fails with peer dependency errors

**Solution:**
```bash
npm install --legacy-peer-deps
```

---

## 📜 All Commands Reference

### 🔧 Setup Commands

```bash
# ==================== BACKEND ====================

# Navigate to backend
cd C:\Jammu\LandOwners\backend

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.\venv\Scripts\activate.bat

# Activate (Linux/Mac)
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install additional packages
pip install pymupdf sentencepiece sacremoses indic-nlp-library huggingface_hub

# Install IndicTransTokenizer
cd C:\Jammu\IndicLLMSuite\IndicTransTokenizer
pip install -e .
cd C:\Jammu\LandOwners\backend

# ==================== FRONTEND ====================

# Navigate to frontend
cd C:\Jammu\LandOwners\frontend

# Install dependencies
npm install

# If peer dependency errors
npm install --legacy-peer-deps
```

### 🔐 HuggingFace Commands

```bash
# Interactive login
huggingface-cli login

# Login with token directly
python -m huggingface_hub.commands.huggingface_cli login --token hf_YOUR_TOKEN

# Check login status
huggingface-cli whoami

# Logout
huggingface-cli logout
```

### ▶️ Running Commands

```bash
# ==================== BACKEND ====================

# Start development server
cd C:\Jammu\LandOwners\backend
.\venv\Scripts\Activate.ps1
python app.py

# Start production server (with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# ==================== FRONTEND ====================

# Start development server
cd C:\Jammu\LandOwners\frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### 🧪 Testing Commands

```bash
# ==================== BACKEND TESTS ====================

cd C:\Jammu\LandOwners\backend

# Test translation
python test_translation.py

# Test RAG processor
python test_rag_processor.py

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# ==================== FRONTEND TESTS ====================

cd C:\Jammu\LandOwners\frontend

# Run tests
npm run test

# Interactive test UI
npm run test:ui

# Coverage report
npm run test:coverage

# Lint code
npm run lint
```

### 🔍 Utility Commands

```bash
# ==================== VERSION CHECK ====================

python --version          # Should be 3.11+
node --version            # Should be 18+
npm --version
tesseract --version
tesseract --list-langs    # Should show eng, hin, urd

# ==================== CACHE MANAGEMENT ====================

# Clear RAG cache (backend)
rm -rf backend/cache/rag/*

# Clear node_modules (frontend)
cd frontend
rm -rf node_modules
npm install

# ==================== DOCKER ====================

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache
```

### 🚀 Quick Start (Copy & Paste)

**Complete setup in one go (Windows PowerShell):**

```powershell
# 1. Backend Setup
cd C:\Jammu\LandOwners\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pymupdf sentencepiece sacremoses indic-nlp-library huggingface_hub

# 2. IndicTransTokenizer
cd C:\Jammu\IndicLLMSuite\IndicTransTokenizer
pip install -e .
cd C:\Jammu\LandOwners\backend

# 3. HuggingFace Login
huggingface-cli login

# 4. Test Translation
python test_translation.py

# 5. Frontend Setup (new terminal)
cd C:\Jammu\LandOwners\frontend
npm install

# 6. Start Backend (Terminal 1)
cd C:\Jammu\LandOwners\backend
.\venv\Scripts\Activate.ps1
python app.py

# 7. Start Frontend (Terminal 2)
cd C:\Jammu\LandOwners\frontend
npm run dev

# 8. Open Browser
start http://localhost:5173
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Read existing documentation files
3. Search GitHub issues
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - System information

---

**Built with ❤️ for digitizing Jammu & Kashmir land records**

*Last Updated: December 2025*

# Quick Start Guide - Land Owners OCR System

Get up and running in 5 minutes! ⚡

## Prerequisites Check

Before you start, make sure you have:

- [ ] Python 3.8 or higher
- [ ] Node.js 20.16 or higher
- [ ] Git installed
- [ ] 2GB free disk space
- [ ] Internet connection (for dependencies)

## Step 1: Clone Repository (30 seconds)

```bash
git clone https://github.com/Bhanu-partap-13/LandOwners.git
cd LandOwners
```

## Step 2: Install Tesseract OCR (2 minutes)

### Windows
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (use default path: `C:\Program Files\Tesseract-OCR\`)
3. Tesseract will be auto-detected

### Linux/Ubuntu
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin tesseract-ocr-urd
```

### macOS
```bash
brew install tesseract tesseract-lang
```

## Step 3: Choose Your Setup Method

### 🐳 Option A: Docker (Easiest - Recommended)

**No Python or Node.js setup needed!**

```bash
# Make sure Docker Desktop is running
docker --version  # Verify Docker is installed

# Deploy everything with one command
./deploy.sh      # Linux/Mac
# OR
deploy.bat       # Windows
```

✅ That's it! Skip to Step 5.

### 💻 Option B: Development Setup (Full Control)

#### Backend Setup (2 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate     # Linux/Mac
# OR
venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env       # Windows
# OR
cp .env.example .env        # Linux/Mac

# Start backend
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

#### Frontend Setup (2 minutes)

**Open a new terminal:**

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
copy .env.example .env       # Windows
# OR
cp .env.example .env        # Linux/Mac

# Start frontend
npm run dev
```

You should see:
```
  VITE ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

## Step 4: Verify Installation

### Test Backend
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

### Test Frontend
Open browser: http://localhost:5173 (dev) or http://localhost (docker)

You should see the "Land Record OCR System" homepage.

## Step 5: Process Your First Document

### Using the Web Interface

1. **Open the application**: http://localhost:5173 (or http://localhost for Docker)

2. **Upload an image**:
   - Drag and drop any image with text
   - Or click "Click to select file"
   - Supported: JPG, PNG, PDF (max 16MB)

3. **Click "Process with OCR"**

4. **Watch the magic happen**:
   - See real-time processing stages
   - View extracted text in multiple tabs
   - Check confidence scores and metadata

5. **Export your results**:
   - Click "Export JSON" to download results
   - Or "Download as TXT" for plain text
   - Or "Copy to Clipboard" for quick use

### Using the API

```bash
# Upload and process in one call
curl -X POST http://localhost:5000/api/ocr/process-upload \
  -F "file=@/path/to/your/image.jpg" \
  -F 'options={"preprocess": true, "clean_text": true}'
```

## Common First-Time Issues

### "Tesseract not found" Error

**Fix**: Update backend/.env with correct Tesseract path:

```env
# Windows
TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe

# Linux
TESSERACT_PATH=/usr/bin/tesseract

# macOS
TESSERACT_PATH=/usr/local/bin/tesseract
```

### "Port already in use" Error

**Fix**: Change the port in configuration:

Backend (backend/config.py):
```python
PORT = 5001  # Change from 5000
```

Frontend (frontend/.env):
```env
VITE_API_URL=http://localhost:5001
```

### "Module not found" Error

**Fix**: Make sure virtual environment is activated:
```bash
# You should see (venv) in your terminal prompt
source venv/bin/activate     # Linux/Mac
venv\Scripts\activate        # Windows
```

### Docker Container Won't Start

**Fix**: Check if ports are available:
```bash
# Stop any existing containers
docker-compose down

# Check running containers
docker ps

# Remove old containers
docker-compose rm
```

## Next Steps

### Explore Features
- ✅ Try different languages (English, Hindi, Urdu)
- ✅ Test batch processing
- ✅ Use the comparison view
- ✅ Check the confidence scoring
- ✅ Export in different formats

### Add Sample Data
Place test images in `data/samples/` for easy testing

### Run Tests
```bash
# Backend
cd backend
pytest tests/

# Frontend
cd frontend
npm test
```

### Customize
- Update Tailwind theme in `frontend/tailwind.config.js`
- Adjust OCR settings in `backend/config.py`
- Add custom preprocessing in `backend/utils/image_processing.py`

## Getting Help

### Check Documentation
- [README.md](README.md) - Full documentation
- [API Documentation](README.md#api-documentation)
- [Integration Testing](INTEGRATION_TESTING.md)
- [Contributing Guide](CONTRIBUTING.md)

### Troubleshooting
1. Check logs:
   ```bash
   # Docker
   docker-compose logs backend
   docker-compose logs frontend
   
   # Development
   tail -f backend/logs/app.log
   ```

2. Verify services:
   ```bash
   # Backend health
   curl http://localhost:5000/api/health
   
   # OCR status
   curl http://localhost:5000/api/ocr/status
   ```

3. Restart services:
   ```bash
   # Docker
   docker-compose restart
   
   # Development
   # Stop with Ctrl+C and restart
   python app.py       # Backend
   npm run dev        # Frontend
   ```

### Community Support
- Open an issue: https://github.com/Bhanu-partap-13/LandOwners/issues
- Check existing issues for solutions

## Stopping the Application

### Docker
```bash
docker-compose down
```

### Development Mode
Press `Ctrl+C` in both terminals (backend and frontend)

## Summary of Commands

### Docker Mode
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f
```

### Development Mode
```bash
# Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py

# Frontend (new terminal)
cd frontend
npm run dev
```

---

## 🎉 Congratulations!

You now have a fully functional OCR system running! Start processing your land records and explore all the features.

**Need help?** Check the [full documentation](README.md) or open an issue on GitHub.

**Ready for production?** See [deployment guide](README.md#deployment).

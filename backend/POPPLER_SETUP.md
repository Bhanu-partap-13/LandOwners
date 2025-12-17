# Poppler Installation Instructions for Windows

## What is Poppler?
Poppler is required for PDF processing in the OCR system. It enables converting PDF files to images for OCR processing.

## Installation Steps

### Option 1: Using Conda (Recommended)
```bash
conda install -c conda-forge poppler
```

### Option 2: Manual Installation

1. **Download Poppler for Windows**
   - Visit: https://github.com/oschwartz10612/poppler-windows/releases/
   - Download the latest release (e.g., `poppler-24.08.0-0.zip`)

2. **Extract Files**
   - Extract to: `C:\Program Files\poppler`
   - You should have folders like: `bin`, `include`, `lib`, `share`

3. **Add to PATH**
   - Open System Properties → Environment Variables
   - Edit "Path" in System Variables
   - Add new entry: `C:\Program Files\poppler\bin`
   - Click OK to save

4. **Verify Installation**
   ```bash
   pdftoppm -v
   ```
   Should output Poppler version information

## Alternative: Using Chocolatey
```bash
choco install poppler
```

## After Installation
Restart your terminal and backend server:
```bash
cd C:\Jammu\LandOwners\backend
python app.py
```

## Troubleshooting

### Error: "poppler not found"
- Ensure the `bin` folder is in PATH
- Restart terminal after adding to PATH
- Check with: `where pdftoppm`

### Error: "Unable to get page count"
- Poppler is not installed or not in PATH
- Try running: `pdftoppm -v` to verify
- Re-add to PATH if needed

## For Linux/Mac

### Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils
```

### macOS:
```bash
brew install poppler
```

## Configuration in Backend

The backend automatically detects poppler. If needed, you can set the path in `.env`:

```env
POPPLER_PATH=C:/Program Files/poppler/bin
```

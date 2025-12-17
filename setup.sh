#!/bin/bash

# Setup Script for Land Owners OCR System
# This script sets up the development environment

set -e

echo "========================================="
echo "Land Owners OCR System - Setup"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version) found${NC}"

# Check Node.js
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version) found${NC}"

# Check Tesseract
echo "Checking Tesseract OCR installation..."
if ! command -v tesseract &> /dev/null; then
    echo -e "${YELLOW}Warning: Tesseract OCR is not installed${NC}"
    echo "Please install Tesseract OCR for the system to work"
    echo "Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin tesseract-ocr-urd"
    echo "macOS: brew install tesseract tesseract-lang"
else
    echo -e "${GREEN}✓ Tesseract $(tesseract --version | head -n1) found${NC}"
fi

# Setup Backend
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}Created backend/.env file. Please update with your settings.${NC}"
fi

# Create directories
mkdir -p uploads temp logs

cd ..

# Setup Frontend
echo ""
echo "Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}Created frontend/.env file. Please update with your settings.${NC}"
fi

cd ..

# Create data directory
mkdir -p data/samples

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your Tesseract path"
echo "2. Start backend: cd backend && source venv/bin/activate && python app.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker:"
echo "  ./deploy.sh"

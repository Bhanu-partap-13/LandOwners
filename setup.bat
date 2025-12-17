@echo off
REM Setup Script for Land Owners OCR System (Windows)

echo =========================================
echo Land Owners OCR System - Setup
echo =========================================

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    exit /b 1
)
python --version
echo [OK] Python found

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed
    exit /b 1
)
node --version
echo [OK] Node.js found

REM Check Tesseract
echo Checking Tesseract OCR installation...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo Warning: Tesseract OCR is not installed
    echo Please download and install from: https://github.com/UB-Mannheim/tesseract/wiki
) else (
    tesseract --version
    echo [OK] Tesseract found
)

REM Setup Backend
echo.
echo Setting up backend...
cd backend

REM Create virtual environment
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file
if not exist .env (
    copy .env.example .env
    echo Created backend\.env file. Please update with your settings.
)

REM Create directories
if not exist uploads mkdir uploads
if not exist temp mkdir temp
if not exist logs mkdir logs

cd ..

REM Setup Frontend
echo.
echo Setting up frontend...
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

REM Create .env file
if not exist .env (
    copy .env.example .env
    echo Created frontend\.env file. Please update with your settings.
)

cd ..

REM Create data directory
if not exist data\samples mkdir data\samples

echo.
echo =========================================
echo Setup completed successfully!
echo =========================================
echo.
echo Next steps:
echo 1. Update backend\.env with your Tesseract path
echo 2. Start backend: cd backend ^&^& venv\Scripts\activate ^&^& python app.py
echo 3. Start frontend: cd frontend ^&^& npm run dev
echo.
echo Or use Docker:
echo   deploy.bat

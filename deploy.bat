@echo off
REM Deployment Script for Land Owners OCR System (Windows)
REM This script builds and deploys the application using Docker

echo =========================================
echo Land Owners OCR System - Deployment
echo =========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker Compose is not installed
    exit /b 1
)

echo [OK] Docker and Docker Compose are installed

REM Check if .env files exist
if not exist backend\.env (
    echo Warning: backend\.env not found
    echo Creating from .env.example...
    copy backend\.env.example backend\.env
)

if not exist frontend\.env (
    echo Warning: frontend\.env not found
    echo Creating from .env.example...
    copy frontend\.env.example frontend\.env
)

REM Build Docker images
echo.
echo Building Docker images...
docker-compose build

REM Stop any running containers
echo.
echo Stopping existing containers...
docker-compose down

REM Start containers
echo.
echo Starting containers...
docker-compose up -d

REM Wait for services to be ready
echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo.
echo Checking service status...
docker-compose ps

REM Test backend health
echo.
echo Testing backend health...
timeout /t 5 /nobreak >nul
curl -f http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend health check failed
    docker-compose logs backend
    exit /b 1
) else (
    echo [OK] Backend health check passed
)

echo.
echo =========================================
echo Deployment completed successfully!
echo =========================================
echo.
echo Application URLs:
echo   Frontend: http://localhost
echo   Backend API: http://localhost:5000
echo   Health Check: http://localhost:5000/api/health
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop services:
echo   docker-compose down

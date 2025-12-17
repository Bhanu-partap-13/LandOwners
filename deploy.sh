#!/bin/bash

# Deployment Script for Land Owners OCR System
# This script builds and deploys the application using Docker

set -e

echo "========================================="
echo "Land Owners OCR System - Deployment"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}Warning: backend/.env not found${NC}"
    echo "Creating from .env.example..."
    cp backend/.env.example backend/.env
fi

if [ ! -f frontend/.env ]; then
    echo -e "${YELLOW}Warning: frontend/.env not found${NC}"
    echo "Creating from .env.example..."
    cp frontend/.env.example frontend/.env
fi

# Build Docker images
echo ""
echo "Building Docker images..."
docker-compose build

# Stop any running containers
echo ""
echo "Stopping existing containers..."
docker-compose down

# Start containers
echo ""
echo "Starting containers..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 10

# Check if services are running
echo ""
echo "Checking service status..."

if docker-compose ps | grep -q "landowners-backend.*Up"; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
    docker-compose logs backend
    exit 1
fi

if docker-compose ps | grep -q "landowners-frontend.*Up"; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend failed to start${NC}"
    docker-compose logs frontend
    exit 1
fi

# Test backend health
echo ""
echo "Testing backend health..."
sleep 5
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    docker-compose logs backend
    exit 1
fi

# Show running containers
echo ""
echo "Running containers:"
docker-compose ps

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Application URLs:"
echo "  Frontend: http://localhost"
echo "  Backend API: http://localhost:5000"
echo "  Health Check: http://localhost:5000/api/health"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"

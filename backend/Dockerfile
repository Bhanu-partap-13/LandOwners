FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs temp cache

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:create_app()"]
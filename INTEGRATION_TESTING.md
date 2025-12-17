# Integration Testing Guide

This guide covers end-to-end integration testing for the Land Owners OCR System.

## Prerequisites

- Backend running on `http://localhost:5000`
- Frontend running on `http://localhost:5173` (or production on port 80)
- Tesseract OCR installed with language packs
- Sample test images in `data/samples/`

## Quick Start

### 1. Run Full System
```bash
# Option A: Development Mode
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev

# Option B: Docker
docker-compose up
```

### 2. Verify Services

#### Backend Health Check
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-17T...",
  "version": "1.0.0"
}
```

#### Frontend Access
Open browser: `http://localhost:5173` (dev) or `http://localhost` (docker)

## Integration Test Scenarios

### Scenario 1: Basic OCR Flow

1. **Upload Image**
   - Navigate to frontend
   - Drag and drop or select an English land record image
   - Verify preview appears

2. **Process Image**
   - Click "Process with OCR"
   - Verify processing status updates in real-time
   - Confirm all stages complete: preprocessing → OCR → detection → cleaning → transliteration

3. **View Results**
   - Check Raw OCR tab shows extracted text
   - Check Cleaned Text tab shows cleaned version
   - Check Transliterated tab (if applicable)
   - Check Metadata shows confidence, language, processing time

4. **Export Results**
   - Test "Export JSON" button
   - Test "Download as TXT" button
   - Test "Copy to Clipboard" button
   - Verify downloads work correctly

### Scenario 2: Multi-Language Support

1. **Test English Document**
   ```bash
   curl -X POST http://localhost:5000/api/ocr/process-upload \
     -F "file=@data/samples/english_printed_01.jpg"
   ```
   - Verify language detected as 'en'
   - Verify confidence > 0.8

2. **Test Hindi Document**
   ```bash
   curl -X POST http://localhost:5000/api/ocr/process-upload \
     -F "file=@data/samples/hindi_printed_01.jpg"
   ```
   - Verify language detected as 'hi'
   - Verify Devanagari script detected

3. **Test Urdu Document**
   ```bash
   curl -X POST http://localhost:5000/api/ocr/process-upload \
     -F "file=@data/samples/urdu_printed_01.jpg"
   ```
   - Verify language detected as 'ur'
   - Verify Urdu script detected
   - Verify transliteration to Roman works

### Scenario 3: Batch Processing

1. **Prepare Multiple Files**
   ```bash
   curl -X POST http://localhost:5000/api/ocr/batch \
     -F "files=@data/samples/english_printed_01.jpg" \
     -F "files=@data/samples/hindi_printed_01.jpg" \
     -F "files=@data/samples/urdu_printed_01.jpg"
   ```

2. **Verify Batch Results**
   - Check total count matches uploaded files
   - Verify all successful
   - Check individual results for each file

### Scenario 4: Error Handling

1. **Invalid File Type**
   ```bash
   curl -X POST http://localhost:5000/api/ocr/process-upload \
     -F "file=@README.md"
   ```
   - Verify 400 error returned
   - Check error message: "Invalid file type"

2. **Missing File**
   ```bash
   curl -X POST http://localhost:5000/api/ocr/upload
   ```
   - Verify 400 error returned
   - Check error message indicates missing file

3. **File Too Large**
   - Upload file > 16MB
   - Verify 413 error returned

### Scenario 5: Comparison View

1. Upload and process an image
2. Navigate to Comparison tab
3. Test different view combinations:
   - Image vs Raw Text
   - Raw Text vs Cleaned Text
   - Cleaned Text vs Transliterated
4. Verify quick comparison buttons work
5. Check diff statistics display correctly

### Scenario 6: Performance and Caching

1. **First Request (No Cache)**
   ```bash
   time curl -X POST http://localhost:5000/api/ocr/process-upload \
     -F "file=@data/samples/test.jpg"
   ```
   - Note processing time

2. **Second Request (Cached)**
   ```bash
   time curl -X POST http://localhost:5000/api/ocr/process-upload \
     -F "file=@data/samples/test.jpg"
   ```
   - Verify faster response
   - Check `from_cache: true` in response

3. **Check Performance Metrics**
   ```bash
   curl http://localhost:5000/api/ocr/status
   ```
   - Verify metrics include cache hit rate
   - Check average processing time

### Scenario 7: Confidence Scoring

1. Upload high-quality image
   - Verify confidence grade 'A' or 'B'
   - Check recommendations show "Good quality"

2. Upload low-quality image
   - Verify confidence grade 'C', 'D', or 'F'
   - Check recommendations suggest improvements

3. Review confidence breakdown:
   - OCR confidence
   - Text quality
   - Language confidence
   - Character density
   - Word validity

### Scenario 8: Dashboard Analytics

1. Process multiple documents
2. Navigate to Dashboard (if implemented in UI)
3. Verify displays:
   - Total documents processed
   - Success rate
   - Average processing time
   - Language distribution chart
   - Processing stage times
   - Quality distribution

## Automated Test Execution

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### API Tests with Newman (Postman CLI)
```bash
# Install Newman
npm install -g newman

# Run API tests (if collection exists)
newman run postman_collection.json
```

## Load Testing

### Using Apache Bench
```bash
# Test single endpoint
ab -n 100 -c 10 http://localhost:5000/api/health

# Test OCR endpoint (requires multipart data)
ab -n 10 -c 2 -T 'multipart/form-data' \
  -p upload_data.txt http://localhost:5000/api/ocr/upload
```

### Using Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class OCRUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def health_check(self):
        self.client.get("/api/health")
    
    @task(3)
    def status_check(self):
        self.client.get("/api/ocr/status")
```

Run:
```bash
pip install locust
locust -f locustfile.py --host=http://localhost:5000
```

## Docker Integration Tests

### Test Container Build
```bash
# Build backend
docker build -t landowners-backend ./backend

# Build frontend
docker build -t landowners-frontend ./frontend

# Verify images
docker images | grep landowners
```

### Test Container Networking
```bash
# Start with docker-compose
docker-compose up -d

# Test backend from frontend container
docker exec landowners-frontend curl http://backend:5000/api/health

# Test logs
docker-compose logs backend
docker-compose logs frontend
```

## Common Issues and Solutions

### Issue: Tesseract not found
**Solution**: Install Tesseract and set correct path in `.env`
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin tesseract-ocr-urd

# Update .env
TESSERACT_PATH=/usr/bin/tesseract
```

### Issue: CORS errors
**Solution**: Check CORS_ORIGINS in backend/config.py matches frontend URL

### Issue: Slow OCR processing
**Solution**: 
- Enable caching
- Reduce image size
- Use batch processing
- Check CPU/GPU availability for TrOCR

### Issue: Frontend can't connect to backend
**Solution**:
- Verify backend is running: `curl http://localhost:5000/api/health`
- Check VITE_API_URL in frontend/.env
- Verify CORS settings

## Deployment Verification

After deploying to production:

1. **Health Checks**
   ```bash
   curl https://your-domain.com/api/health
   ```

2. **SSL Certificate**
   ```bash
   curl -I https://your-domain.com
   ```

3. **Performance**
   - Monitor response times
   - Check error rates
   - Verify caching works

4. **Logs**
   ```bash
   # Docker
   docker-compose logs -f --tail=100
   
   # Direct
   tail -f backend/logs/app.log
   ```

## Success Criteria

- [ ] All API endpoints return expected responses
- [ ] Frontend loads without errors
- [ ] Can upload and process images
- [ ] All languages detected correctly
- [ ] Export functionality works
- [ ] Caching improves performance
- [ ] Error messages are clear and helpful
- [ ] Tests pass with >90% coverage
- [ ] Docker deployment works
- [ ] Documentation is complete

## Reporting Issues

When reporting integration issues, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Screenshots/logs
4. Environment details (OS, versions)
5. Network/API call details

## Next Steps

After successful integration testing:
1. Set up CI/CD pipeline
2. Configure monitoring and alerting
3. Implement backup strategy
4. Plan scaling strategy
5. Train users on the system

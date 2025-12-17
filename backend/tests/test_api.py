"""
API Endpoint Tests
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from io import BytesIO


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestAPIEndpoints:
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_status_endpoint(self, client):
        """Test OCR status endpoint"""
        response = client.get('/api/ocr/status')
        assert response.status_code == 200
        data = response.get_json()
        assert 'service' in data['data']
    
    def test_upload_no_file(self, client):
        """Test upload without file"""
        response = client.post('/api/ocr/upload')
        assert response.status_code == 400
    
    def test_upload_invalid_file(self, client):
        """Test upload with invalid file type"""
        data = {
            'file': (BytesIO(b'test data'), 'test.txt')
        }
        response = client.post(
            '/api/ocr/upload',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

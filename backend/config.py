"""
Configuration module for Land Record OCR Backend
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_APP = os.environ.get('FLASK_APP') or 'app.py'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # File upload settings
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'uploads'))
    TEMP_FOLDER = os.path.join(BASE_DIR, os.environ.get('TEMP_FOLDER', 'temp'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,pdf').split(','))
    
    # OCR settings - Auto-detect Tesseract path
    TESSERACT_PATH = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX', os.path.join(BASE_DIR, 'tessdata'))
    TESSERACT_LANG = 'eng+hin+urd'  # English, Hindi, Urdu
    
    # Model paths
    SETU_PATH = os.environ.get('SETU_PATH', '../IndicLLMSuite/setu')
    SETU_TRANSLATE_PATH = os.environ.get('SETU_TRANSLATE_PATH', '../IndicLLMSuite/setu-translate')
    URDU_OCR_MODEL = 'microsoft/trocr-base-handwritten'  # Hugging Face model
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173']
    
    # Processing settings
    OCR_CONFIDENCE_THRESHOLD = 60  # Minimum confidence score
    IMAGE_MAX_SIZE = (3000, 3000)  # Maximum image dimensions
    BATCH_SIZE = 10  # Maximum images in batch
    
    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

"""
Configuration module for Land Record OCR Backend
LIGHTWEIGHT VERSION - Uses cloud APIs instead of local models
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
    
    # =========================================
    # AI4BHARAT SETTINGS (Self-hosted Translation)
    # =========================================
    # Uses IndicTrans2 and IndicXlit models locally
    # No external API required - runs completely offline!
    # Models are downloaded automatically on first use
    # 
    # IndicTrans2: ~800MB (translation)
    # IndicXlit: ~50MB (transliteration)
    AI4BHARAT_CACHE_DIR = os.environ.get('AI4BHARAT_CACHE_DIR', os.path.join(BASE_DIR, 'models', 'ai4bharat'))
    AI4BHARAT_DEVICE = os.environ.get('AI4BHARAT_DEVICE', 'auto')  # 'auto', 'cpu', or 'cuda'
    
    # =========================================
    # GOOGLE CLOUD VISION (Optional OCR - 1000 free/month)
    # =========================================
    # Setup: https://console.cloud.google.com
    # Enable: Cloud Vision API (only needed for OCR, not translation)
    GOOGLE_CLOUD_API_KEY = os.environ.get('GOOGLE_CLOUD_API_KEY', '')
    
    # =========================================
    # LEGACY SETTINGS (for backward compatibility)
    # =========================================
    # These are kept for compatibility but NOT REQUIRED in lightweight mode
    TESSERACT_PATH = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX', os.path.join(BASE_DIR, 'tessdata'))
    TESSERACT_LANG = 'eng+hin+urd'  # English, Hindi, Urdu
    
    # Model paths (NOT REQUIRED in lightweight mode)
    SETU_PATH = os.environ.get('SETU_PATH', '../IndicLLMSuite/setu')
    SETU_TRANSLATE_PATH = os.environ.get('SETU_TRANSLATE_PATH', '../IndicLLMSuite/setu-translate')
    URDU_OCR_MODEL = 'microsoft/trocr-base-handwritten'  # Not used in lightweight mode
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173']
    
    # Processing settings
    OCR_CONFIDENCE_THRESHOLD = 60  # Minimum confidence score
    IMAGE_MAX_SIZE = (3000, 3000)  # Maximum image dimensions
    BATCH_SIZE = 10  # Maximum images in batch
    
    # OCR Mode: 'lightweight' (cloud API) or 'local' (Tesseract)
    OCR_MODE = os.environ.get('OCR_MODE', 'lightweight')
    
    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)
    
    @staticmethod
    def is_ai4bharat_available():
        """Check if AI4Bharat models are available"""
        try:
            import torch
            from transformers import AutoModelForSeq2SeqLM
            return True
        except ImportError:
            return False
    
    @staticmethod  
    def is_google_vision_configured():
        """Check if Google Vision API is configured"""
        return bool(Config.GOOGLE_CLOUD_API_KEY)
    
    @staticmethod
    def get_ai4bharat_device():
        """Get device for AI4Bharat models"""
        device = Config.AI4BHARAT_DEVICE
        if device == 'auto':
            try:
                import torch
                return 'cuda' if torch.cuda.is_available() else 'cpu'
            except ImportError:
                return 'cpu'
        return device

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

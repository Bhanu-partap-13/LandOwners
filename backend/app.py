"""
Land Record OCR - Flask Application
Main entry point for the OCR backend API
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
import logging
import os

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Land Record OCR API',
            'version': '2.0.0',  # Lightweight version
            'status': 'running',
            'mode': 'lightweight'
        })
    
    @app.route('/api/health')
    def health():
        from config import Config
        return jsonify({
            'status': 'healthy',
            'service': 'OCR Backend (AI4Bharat)',
            'mode': Config.OCR_MODE,
            'ai4bharat_available': Config.is_ai4bharat_available(),
            'ai4bharat_device': Config.get_ai4bharat_device(),
            'google_vision_configured': Config.is_google_vision_configured(),
            'backends_available': _get_available_backends()
        })
    
    def _get_available_backends():
        """Check which OCR/translation backends are available"""
        backends = []
        from config import Config
        if Config.is_ai4bharat_available():
            backends.append('ai4bharat')
        if Config.is_google_vision_configured():
            backends.append('google_vision')
        # Always include dictionary-based translation
        backends.append('dictionary')
        return backends
    
    return app

def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # File handler
        file_handler = logging.FileHandler('logs/ocr_backend.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Land Record OCR Backend startup')

def register_blueprints(app):
    """Register application blueprints"""
    from routes.ocr_routes import ocr_bp
    from routes.translation_routes import translation_bp
    from routes.rag_routes import rag_bp
    
    app.register_blueprint(ocr_bp, url_prefix='/api/ocr')
    app.register_blueprint(translation_bp, url_prefix='/api/translate')
    app.register_blueprint(rag_bp, url_prefix='/api/rag')

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'error': 'File size exceeds maximum limit'}), 413

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

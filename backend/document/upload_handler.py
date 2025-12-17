"""
File upload handler with validation and security
"""
import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import logging
from config import Config

logger = logging.getLogger(__name__)

class UploadHandler:
    """Handle file uploads with validation and security"""
    
    def __init__(self, upload_folder=None, allowed_extensions=None, max_file_size=None):
        """
        Initialize upload handler
        
        Args:
            upload_folder: Directory to save uploads
            allowed_extensions: Set of allowed file extensions
            max_file_size: Maximum file size in bytes
        """
        self.upload_folder = upload_folder or Config.UPLOAD_FOLDER
        self.allowed_extensions = allowed_extensions or Config.ALLOWED_EXTENSIONS
        self.max_file_size = max_file_size or Config.MAX_CONTENT_LENGTH
        
        # Ensure upload folder exists
        os.makedirs(self.upload_folder, exist_ok=True)
        
        logger.info(f"Upload handler initialized: {self.upload_folder}")
    
    def allowed_file(self, filename):
        """
        Check if file extension is allowed
        
        Args:
            filename: Name of the file
        
        Returns:
            bool: True if extension is allowed
        """
        if '.' not in filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in self.allowed_extensions
    
    def validate_file(self, file):
        """
        Validate uploaded file
        
        Args:
            file: FileStorage object
        
        Returns:
            dict: Validation result
        """
        if not file:
            return {
                'valid': False,
                'error': 'No file provided'
            }
        
        if file.filename == '':
            return {
                'valid': False,
                'error': 'Empty filename'
            }
        
        if not self.allowed_file(file.filename):
            return {
                'valid': False,
                'error': f'File type not allowed. Allowed types: {", ".join(self.allowed_extensions)}'
            }
        
        # Check file size (if available)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.max_file_size:
            return {
                'valid': False,
                'error': f'File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB'
            }
        
        return {
            'valid': True,
            'filename': file.filename,
            'size': file_size,
            'extension': file.filename.rsplit('.', 1)[1].lower()
        }
    
    def save_file(self, file, custom_filename=None):
        """
        Save uploaded file securely
        
        Args:
            file: FileStorage object
            custom_filename: Optional custom filename (without extension)
        
        Returns:
            dict: Save result with file path
        """
        # Validate file first
        validation = self.validate_file(file)
        
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['error']
            }
        
        try:
            # Generate unique filename
            if custom_filename:
                filename = secure_filename(custom_filename)
            else:
                unique_id = str(uuid.uuid4())
                original_filename = secure_filename(file.filename)
                name, ext = os.path.splitext(original_filename)
                filename = f"{unique_id}_{name}{ext}"
            
            # Full path
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save file
            file.save(filepath)
            
            logger.info(f"File saved: {filepath}")
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'size': validation['size'],
                'extension': validation['extension']
            }
        
        except Exception as e:
            logger.error(f"File save failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, filepath):
        """
        Delete uploaded file
        
        Args:
            filepath: Path to file
        
        Returns:
            bool: Success status
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"File deleted: {filepath}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return False
    
    def get_file_info(self, filepath):
        """Get information about a file"""
        if not os.path.exists(filepath):
            return None
        
        stat = os.stat(filepath)
        
        return {
            'path': filepath,
            'filename': os.path.basename(filepath),
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'extension': os.path.splitext(filepath)[1][1:]
        }
    
    def cleanup_old_files(self, max_age_hours=24):
        """
        Clean up old uploaded files
        
        Args:
            max_age_hours: Maximum age of files to keep (in hours)
        
        Returns:
            int: Number of files deleted
        """
        import time
        
        deleted_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for filename in os.listdir(self.upload_folder):
                filepath = os.path.join(self.upload_folder, filename)
                
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return deleted_count

class PDFHandler:
    """Handle PDF file conversion to images"""
    
    def __init__(self):
        self.available = False
        self.method = None
        
        # Try PyMuPDF first (faster, no external dependencies)
        try:
            import fitz
            self.fitz = fitz
            self.available = True
            self.method = 'pymupdf'
            logger.info("PDFHandler initialized with PyMuPDF")
        except ImportError:
            # Fallback to pdf2image (requires poppler)
            try:
                from pdf2image import convert_from_path
                self.convert_from_path = convert_from_path
                self.available = True
                self.method = 'pdf2image'
                logger.info("PDFHandler initialized with pdf2image")
            except ImportError:
                logger.warning("No PDF conversion library available (install pymupdf or pdf2image)")
    
    def pdf_to_images(self, pdf_path, output_folder=None):
        """
        Convert PDF pages to images
        
        Args:
            pdf_path: Path to PDF file
            output_folder: Folder to save images (optional)
        
        Returns:
            list: Paths to generated images
        """
        if not self.available:
            raise RuntimeError("No PDF conversion library installed")
        
        image_paths = []
        
        try:
            if output_folder is None:
                output_folder = os.path.dirname(pdf_path)
            
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            if self.method == 'pymupdf':
                doc = self.fitz.open(pdf_path)
                for i, page in enumerate(doc):
                    # Render page to image (300 DPI = 4.166 scale)
                    pix = page.get_pixmap(matrix=self.fitz.Matrix(300/72, 300/72))
                    
                    image_filename = f"{base_name}_page_{i+1}.png"
                    image_path = os.path.join(output_folder, image_filename)
                    
                    pix.save(image_path)
                    image_paths.append(image_path)
                doc.close()
                
            elif self.method == 'pdf2image':
                # Convert PDF to images
                images = self.convert_from_path(pdf_path, dpi=300)
                
                for i, image in enumerate(images):
                    image_filename = f"{base_name}_page_{i+1}.png"
                    image_path = os.path.join(output_folder, image_filename)
                    
                    image.save(image_path, 'PNG')
                    image_paths.append(image_path)
            
            return image_paths
            
        except Exception as e:
            logger.error(f"PDF conversion failed: {str(e)}")
            raise
            image_paths = []
            pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for i, image in enumerate(images):
                image_filename = f"{pdf_basename}_page_{i+1}.png"
                image_path = os.path.join(output_folder, image_filename)
                image.save(image_path, 'PNG')
                image_paths.append(image_path)
            
            logger.info(f"Converted PDF to {len(image_paths)} images")
            return image_paths
        
        except Exception as e:
            logger.error(f"PDF conversion failed: {str(e)}")
            raise

def get_mime_type(filepath):
    """Get MIME type of a file"""
    import mimetypes
    
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type or 'application/octet-stream'

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

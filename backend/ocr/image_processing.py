"""
Image preprocessing utilities for OCR enhancement
Uses OpenCV to improve image quality before OCR processing
"""
import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """Handles all image preprocessing operations for OCR"""
    
    def __init__(self):
        self.processing_history = []
    
    def preprocess(self, image_path, operations=None):
        """
        Main preprocessing pipeline
        
        Args:
            image_path: Path to input image
            operations: List of operations to perform (default: all)
                       ['grayscale', 'denoise', 'contrast', 'deskew', 'binarize']
        
        Returns:
            Preprocessed image (numpy array)
        """
        if operations is None:
            operations = ['grayscale', 'denoise', 'contrast', 'deskew', 'binarize']
        
        logger.info(f"Starting preprocessing for: {image_path}")
        self.processing_history = []
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        self.processing_history.append(f"Loaded image: {image.shape}")
        
        # Apply operations in sequence
        if 'grayscale' in operations:
            image = self.to_grayscale(image)
        
        if 'denoise' in operations:
            image = self.denoise(image)
        
        if 'contrast' in operations:
            image = self.enhance_contrast(image)
        
        if 'deskew' in operations:
            image = self.deskew(image)
        
        if 'binarize' in operations:
            image = self.binarize(image)
        
        logger.info(f"Preprocessing complete: {len(self.processing_history)} operations")
        return image
    
    def to_grayscale(self, image):
        """Convert image to grayscale"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.processing_history.append("Converted to grayscale")
            return gray
        return image
    
    def denoise(self, image):
        """Remove noise from image"""
        # Use Non-local Means Denoising
        if len(image.shape) == 2:  # Grayscale
            denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        else:  # Color
            denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        self.processing_history.append("Applied denoising")
        return denoised
    
    def enhance_contrast(self, image):
        """Enhance image contrast using CLAHE"""
        if len(image.shape) == 3:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        else:
            # Apply CLAHE directly for grayscale
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image)
        
        self.processing_history.append("Enhanced contrast (CLAHE)")
        return enhanced
    
    def deskew(self, image):
        """Detect and correct skew in image"""
        # Ensure grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is not None and len(lines) > 0:
            # Calculate average angle
            angles = []
            for rho, theta in lines[:, 0]:
                angle = np.degrees(theta) - 90
                if -45 < angle < 45:
                    angles.append(angle)
            
            if angles:
                median_angle = np.median(angles)
                
                # Only deskew if angle is significant
                if abs(median_angle) > 0.5:
                    # Get rotation matrix
                    h, w = image.shape[:2]
                    center = (w // 2, h // 2)
                    matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    
                    # Rotate image
                    deskewed = cv2.warpAffine(
                        image, matrix, (w, h),
                        flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_REPLICATE
                    )
                    
                    self.processing_history.append(f"Deskewed by {median_angle:.2f}°")
                    return deskewed
        
        self.processing_history.append("No significant skew detected")
        return image
    
    def binarize(self, image):
        """Convert image to binary (black and white)"""
        # Ensure grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Otsu's thresholding
        _, binary = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # Alternative: Adaptive thresholding (better for varying lighting)
        # binary = cv2.adaptiveThreshold(
        #     gray, 255,
        #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #     cv2.THRESH_BINARY, 11, 2
        # )
        
        self.processing_history.append("Applied Otsu's binarization")
        return binary
    
    def resize_image(self, image, max_width=3000, max_height=3000):
        """Resize image while maintaining aspect ratio"""
        h, w = image.shape[:2]
        
        if w > max_width or h > max_height:
            scaling_factor = min(max_width / w, max_height / h)
            new_w = int(w * scaling_factor)
            new_h = int(h * scaling_factor)
            
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            self.processing_history.append(f"Resized from {w}x{h} to {new_w}x{new_h}")
            return resized
        
        return image
    
    def remove_borders(self, image, border_threshold=10):
        """Remove white borders from image"""
        # Ensure grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Find non-white regions
        _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
        coords = cv2.findNonZero(thresh)
        
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            cropped = image[y:y+h, x:x+w]
            self.processing_history.append(f"Removed borders: cropped to {w}x{h}")
            return cropped
        
        return image
    
    def get_processing_info(self):
        """Return information about processing steps"""
        return {
            'steps': self.processing_history,
            'total_operations': len(self.processing_history)
        }

def save_image(image, output_path):
    """Save processed image to file"""
    cv2.imwrite(output_path, image)
    logger.info(f"Saved processed image to: {output_path}")

def image_to_pil(cv_image):
    """Convert OpenCV image to PIL Image"""
    if len(cv_image.shape) == 2:  # Grayscale
        return Image.fromarray(cv_image)
    else:  # Color
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)

def pil_to_cv(pil_image):
    """Convert PIL Image to OpenCV image"""
    numpy_image = np.array(pil_image)
    if len(numpy_image.shape) == 2:  # Grayscale
        return numpy_image
    else:  # Color
        return cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

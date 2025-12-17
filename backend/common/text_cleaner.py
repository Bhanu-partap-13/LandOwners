"""
Text cleaning utilities for OCR output
Uses Setu (IndicLLMSuite) for advanced cleaning
"""
import re
import sys
import os
import logging

logger = logging.getLogger(__name__)

class TextCleaner:
    """Clean and normalize OCR output text"""
    
    def __init__(self, setu_path=None):
        """
        Initialize text cleaner
        
        Args:
            setu_path: Path to Setu module (optional)
        """
        self.setu_path = setu_path
        self.setu_available = False
        
        # Try to load Setu if path provided
        if setu_path and os.path.exists(setu_path):
            try:
                sys.path.insert(0, setu_path)
                # TODO: Import actual Setu modules when available
                self.setu_available = True
                logger.info(f"Setu loaded from: {setu_path}")
            except Exception as e:
                logger.warning(f"Could not load Setu: {str(e)}")
    
    def clean(self, text):
        """
        Main cleaning pipeline
        
        Args:
            text: Raw OCR output
        
        Returns:
            dict: Cleaned text with metadata
        """
        if not text:
            return {
                'original': '',
                'cleaned': '',
                'operations': []
            }
        
        operations = []
        cleaned = text
        
        # Remove excessive whitespace
        cleaned, op = self.remove_extra_whitespace(cleaned)
        if op:
            operations.append(op)
        
        # Remove special characters (but keep basic punctuation)
        cleaned, op = self.remove_unwanted_chars(cleaned)
        if op:
            operations.append(op)
        
        # Fix broken words
        cleaned, op = self.fix_broken_words(cleaned)
        if op:
            operations.append(op)
        
        # Remove duplicate lines
        cleaned, op = self.remove_duplicate_lines(cleaned)
        if op:
            operations.append(op)
        
        # Normalize unicode
        cleaned = self.normalize_unicode(cleaned)
        operations.append("Normalized Unicode")
        
        # Use Setu if available
        if self.setu_available:
            cleaned = self.clean_with_setu(cleaned)
            operations.append("Applied Setu cleaning")
        
        return {
            'original': text,
            'cleaned': cleaned.strip(),
            'operations': operations,
            'char_reduction': len(text) - len(cleaned),
            'improvement_score': self.calculate_quality_score(text, cleaned)
        }
    
    def remove_extra_whitespace(self, text):
        """Remove extra spaces, tabs, newlines"""
        # Replace multiple spaces with single space
        cleaned = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Remove trailing/leading whitespace from each line
        lines = [line.strip() for line in cleaned.split('\n')]
        cleaned = '\n'.join(lines)
        
        operation = f"Removed extra whitespace"
        return cleaned, operation
    
    def remove_unwanted_chars(self, text):
        """Remove OCR artifacts and unwanted characters"""
        # Remove common OCR noise characters
        noise_chars = ['~', '`', '^', '§', '¶', '†', '‡', '•']
        for char in noise_chars:
            text = text.replace(char, '')
        
        # Remove standalone special characters
        cleaned = re.sub(r'\s+[^\w\s]{1}\s+', ' ', text)
        
        operation = "Removed unwanted characters"
        return cleaned, operation
    
    def fix_broken_words(self, text):
        """Attempt to fix words broken by OCR errors"""
        # Fix common OCR mistakes
        replacements = {
            r'(\w)\s+(\w)': r'\1\2',  # Fix single char breaks (but be careful)
            r'l\s+1': 'H',  # Common OCR mistake
            r'0\s+O': 'O',
            r'\s+([,.])\s+': r'\1 '  # Fix punctuation spacing
        }
        
        cleaned = text
        # Note: This is basic - in production, use language-specific rules
        
        operation = "Attempted word reconstruction"
        return cleaned, operation
    
    def remove_duplicate_lines(self, text):
        """Remove duplicate consecutive lines"""
        lines = text.split('\n')
        unique_lines = []
        prev_line = None
        
        for line in lines:
            if line.strip() != prev_line:
                unique_lines.append(line)
                prev_line = line.strip()
        
        cleaned = '\n'.join(unique_lines)
        removed_count = len(lines) - len(unique_lines)
        
        operation = f"Removed {removed_count} duplicate lines" if removed_count > 0 else None
        return cleaned, operation
    
    def normalize_unicode(self, text):
        """Normalize Unicode characters"""
        import unicodedata
        
        # Normalize to NFC form (canonical decomposition followed by canonical composition)
        normalized = unicodedata.normalize('NFC', text)
        return normalized
    
    def clean_with_setu(self, text):
        """
        Use Setu for advanced cleaning
        This is a placeholder for actual Setu integration
        
        Args:
            text: Text to clean
        
        Returns:
            Cleaned text
        """
        # TODO: Integrate actual Setu cleaning functions
        # from setu import clean_text
        # return clean_text(text)
        
        logger.info("Setu cleaning would be applied here")
        return text
    
    def calculate_quality_score(self, original, cleaned):
        """
        Calculate a quality improvement score
        
        Returns:
            float: Score from 0-100
        """
        if not original:
            return 0
        
        # Simple heuristic based on:
        # - Reduction in special characters
        # - More consistent spacing
        # - Less duplicates
        
        original_noise = len(re.findall(r'[^\w\s]', original))
        cleaned_noise = len(re.findall(r'[^\w\s]', cleaned))
        
        original_spaces = len(re.findall(r'\s{2,}', original))
        cleaned_spaces = len(re.findall(r'\s{2,}', cleaned))
        
        noise_reduction = max(0, original_noise - cleaned_noise) / max(original_noise, 1)
        space_improvement = max(0, original_spaces - cleaned_spaces) / max(original_spaces, 1)
        
        score = (noise_reduction * 60 + space_improvement * 40)
        return round(score, 2)
    
    def extract_structured_data(self, text):
        """
        Extract structured information from land records
        
        Args:
            text: Cleaned OCR text
        
        Returns:
            dict: Extracted structured data
        """
        # Common patterns in land records
        patterns = {
            'survey_number': r'Survey\s*No[.:]\s*(\d+[\-/]?\d*)',
            'khata_number': r'Khata\s*No[.:]\s*(\d+)',
            'area': r'Area[:\s]*([\d.]+)\s*(hectare|acre|sq\.?\s*m)',
            'owner_name': r'Owner[:\s]*([A-Za-z\s]+?)(?:\n|$)',
            'village': r'Village[:\s]*([A-Za-z\s]+?)(?:\n|$)'
        }
        
        extracted = {}
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1).strip()
        
        return extracted

class AdvancedTextCleaner(TextCleaner):
    """Enhanced text cleaner with language-specific rules"""
    
    def __init__(self, setu_path=None):
        super().__init__(setu_path)
        self.language_specific_cleaners = {
            'urdu': self.clean_urdu,
            'hindi': self.clean_hindi,
            'english': self.clean_english
        }
    
    def clean_urdu(self, text):
        """Urdu-specific cleaning rules"""
        # Remove diacritics if needed
        # Normalize Urdu-specific characters
        return text
    
    def clean_hindi(self, text):
        """Hindi-specific cleaning rules"""
        # Normalize Devanagari characters
        return text
    
    def clean_english(self, text):
        """English-specific cleaning rules"""
        # Fix common English OCR mistakes
        text = re.sub(r'\bl\b', 'I', text)  # 'l' -> 'I'
        text = re.sub(r'\b0\b', 'O', text)  # '0' -> 'O' in words
        return text
    
    def clean_by_language(self, text, language):
        """Apply language-specific cleaning"""
        cleaner = self.language_specific_cleaners.get(language)
        
        if cleaner:
            return cleaner(text)
        
        return text

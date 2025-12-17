"""
Confidence Scoring System
Evaluates OCR quality and provides confidence metrics
"""

import re
from typing import Dict, List, Tuple
import numpy as np


class ConfidenceScorer:
    """Calculates confidence scores for OCR results"""
    
    def __init__(self):
        self.weights = {
            'ocr_confidence': 0.3,
            'text_quality': 0.2,
            'language_confidence': 0.15,
            'character_density': 0.15,
            'word_validity': 0.2
        }
    
    def calculate_overall_confidence(self, ocr_result: Dict) -> Dict:
        """
        Calculate overall confidence score for OCR result
        
        Args:
            ocr_result: Dictionary containing OCR results and metadata
            
        Returns:
            Dictionary with confidence scores and breakdown
        """
        scores = {}
        
        # OCR engine confidence
        scores['ocr_confidence'] = self._get_ocr_confidence(ocr_result)
        
        # Text quality metrics
        scores['text_quality'] = self._calculate_text_quality(ocr_result.get('raw_text', ''))
        
        # Language detection confidence
        scores['language_confidence'] = self._get_language_confidence(ocr_result)
        
        # Character density (how dense the text is)
        scores['character_density'] = self._calculate_character_density(ocr_result)
        
        # Word validity (how many recognizable words)
        scores['word_validity'] = self._calculate_word_validity(ocr_result.get('raw_text', ''))
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[key] * self.weights[key] 
            for key in self.weights.keys()
        )
        
        return {
            'overall': round(overall_score, 3),
            'breakdown': {k: round(v, 3) for k, v in scores.items()},
            'grade': self._get_grade(overall_score),
            'recommendations': self._get_recommendations(scores)
        }
    
    def _get_ocr_confidence(self, ocr_result: Dict) -> float:
        """Extract OCR engine's confidence score"""
        metadata = ocr_result.get('metadata', {})
        confidence = metadata.get('ocr_confidence', metadata.get('confidence', 0.5))
        
        # Normalize to 0-1 range
        if confidence > 1:
            confidence = confidence / 100.0
        
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_text_quality(self, text: str) -> float:
        """
        Calculate text quality based on various factors
        - Ratio of alphanumeric to special characters
        - Presence of common OCR errors
        - Text coherence
        """
        if not text or len(text) < 10:
            return 0.0
        
        # Remove whitespace for analysis
        text_clean = text.replace(' ', '').replace('\n', '')
        
        if len(text_clean) == 0:
            return 0.0
        
        # Calculate alphanumeric ratio
        alphanum_count = sum(c.isalnum() for c in text_clean)
        alphanum_ratio = alphanum_count / len(text_clean)
        
        # Check for common OCR errors
        error_patterns = [
            r'[|]{2,}',  # Multiple pipes
            r'[_]{3,}',  # Multiple underscores
            r'[~]{2,}',  # Multiple tildes
            r'[\^\*]{2,}',  # Multiple special chars
        ]
        
        error_count = sum(
            len(re.findall(pattern, text)) 
            for pattern in error_patterns
        )
        error_penalty = min(error_count * 0.05, 0.3)
        
        # Check for excessive special characters
        special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in text) / len(text)
        special_char_penalty = min(special_char_ratio * 0.5, 0.2)
        
        quality_score = alphanum_ratio - error_penalty - special_char_penalty
        
        return min(max(quality_score, 0.0), 1.0)
    
    def _get_language_confidence(self, ocr_result: Dict) -> float:
        """Get language detection confidence"""
        language_info = ocr_result.get('language', {})
        confidence = language_info.get('confidence', 0.5)
        
        # Normalize to 0-1 range
        if confidence > 1:
            confidence = confidence / 100.0
        
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_character_density(self, ocr_result: Dict) -> float:
        """
        Calculate character density
        Higher density usually indicates better OCR
        """
        text = ocr_result.get('raw_text', '')
        if not text:
            return 0.0
        
        # Calculate characters per line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return 0.0
        
        avg_chars_per_line = sum(len(line) for line in lines) / len(lines)
        
        # Normalize (typical line has 40-80 characters)
        if avg_chars_per_line < 10:
            density = avg_chars_per_line / 10
        elif avg_chars_per_line > 100:
            density = 1.0 - ((avg_chars_per_line - 100) / 200)
        else:
            density = 0.5 + (avg_chars_per_line - 10) / 180
        
        return min(max(density, 0.0), 1.0)
    
    def _calculate_word_validity(self, text: str) -> float:
        """
        Calculate what percentage of words look valid
        Valid words: 2+ characters, mostly alphanumeric
        """
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        valid_words = 0
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            # Check if valid (2+ chars, mostly letters)
            if len(clean_word) >= 2:
                letter_count = sum(c.isalpha() for c in clean_word)
                if letter_count / len(clean_word) >= 0.5:
                    valid_words += 1
        
        return valid_words / len(words)
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def _get_recommendations(self, scores: Dict) -> List[str]:
        """Provide recommendations based on low scores"""
        recommendations = []
        
        if scores['ocr_confidence'] < 0.6:
            recommendations.append("OCR confidence is low. Try improving image quality or preprocessing.")
        
        if scores['text_quality'] < 0.6:
            recommendations.append("Text quality is poor. Image may have noise or low resolution.")
        
        if scores['language_confidence'] < 0.6:
            recommendations.append("Language detection uncertain. Verify detected language is correct.")
        
        if scores['character_density'] < 0.5:
            recommendations.append("Low character density. Image may be poorly scanned or have large margins.")
        
        if scores['word_validity'] < 0.6:
            recommendations.append("Many invalid words detected. Consider manual review and correction.")
        
        if not recommendations:
            recommendations.append("Good quality OCR result. No major issues detected.")
        
        return recommendations


class BatchConfidenceAnalyzer:
    """Analyze confidence across multiple OCR results"""
    
    def __init__(self):
        self.scorer = ConfidenceScorer()
    
    def analyze_batch(self, results: List[Dict]) -> Dict:
        """
        Analyze confidence scores for a batch of results
        
        Args:
            results: List of OCR result dictionaries
            
        Returns:
            Dictionary with batch statistics
        """
        if not results:
            return {
                'total_documents': 0,
                'average_confidence': 0.0,
                'grade_distribution': {},
                'low_confidence_count': 0
            }
        
        scores = []
        grades = []
        
        for result in results:
            confidence = self.scorer.calculate_overall_confidence(result)
            scores.append(confidence['overall'])
            grades.append(confidence['grade'])
        
        # Calculate statistics
        grade_dist = {grade: grades.count(grade) for grade in set(grades)}
        low_confidence = sum(1 for s in scores if s < 0.6)
        
        return {
            'total_documents': len(results),
            'average_confidence': round(np.mean(scores), 3),
            'median_confidence': round(np.median(scores), 3),
            'std_deviation': round(np.std(scores), 3),
            'min_confidence': round(min(scores), 3),
            'max_confidence': round(max(scores), 3),
            'grade_distribution': grade_dist,
            'low_confidence_count': low_confidence,
            'low_confidence_percentage': round(low_confidence / len(results) * 100, 1)
        }


def test_confidence_scorer():
    """Test the confidence scorer"""
    scorer = ConfidenceScorer()
    
    # Test with sample result
    sample_result = {
        'raw_text': 'This is a sample text from OCR processing.',
        'cleaned_text': 'This is a sample text from OCR processing.',
        'language': {'detected': 'en', 'confidence': 0.95},
        'metadata': {'ocr_confidence': 0.88}
    }
    
    confidence = scorer.calculate_overall_confidence(sample_result)
    print("Confidence Analysis:")
    print(f"Overall Score: {confidence['overall']}")
    print(f"Grade: {confidence['grade']}")
    print("\nBreakdown:")
    for key, value in confidence['breakdown'].items():
        print(f"  {key}: {value}")
    print("\nRecommendations:")
    for rec in confidence['recommendations']:
        print(f"  - {rec}")


if __name__ == '__main__':
    test_confidence_scorer()

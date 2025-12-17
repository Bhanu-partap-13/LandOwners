"""
PDF Generation Utility
Generates PDF documents from translated text
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from typing import Dict, Optional
import os


class PDFGenerator:
    """Generates PDF documents from translated text"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=16
        ))
        
        # Field label style
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            fontName='Helvetica-Bold'
        ))
        
        # Field value style
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#1f2937'),
        ))
    
    def generate_translation_pdf(self, translation_data: Dict, 
                                output_path: Optional[str] = None) -> BytesIO:
        """
        Generate PDF from translation data
        
        Args:
            translation_data: Dictionary containing translation results
            output_path: Optional file path to save PDF
            
        Returns:
            BytesIO buffer containing PDF
        """
        # Create buffer
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Add header
        story.extend(self._add_header())
        
        # Add document information
        story.extend(self._add_document_info(translation_data))
        
        # Add original text section
        if translation_data.get('original'):
            story.extend(self._add_original_section(translation_data['original']))
        
        # Add translated text section
        if translation_data.get('translated'):
            story.extend(self._add_translated_section(translation_data['translated']))
        
        # Add metadata section
        if translation_data.get('metadata'):
            story.extend(self._add_metadata_section(translation_data['metadata']))
        
        # Add footer
        story.extend(self._add_footer())
        
        # Build PDF
        doc.build(story)
        
        # Return buffer
        if not output_path:
            buffer.seek(0)
            return buffer
        
        return None
    
    def _add_header(self):
        """Add PDF header"""
        elements = []
        
        # Title
        title = Paragraph(
            "LAND RECORD TRANSLATION",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph(
            "Official Translation from Urdu to English",
            self.styles['Normal']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Horizontal line
        elements.append(self._create_horizontal_line())
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _add_document_info(self, translation_data: Dict):
        """Add document information section"""
        elements = []
        
        # Get metadata
        metadata = translation_data.get('metadata', {})
        
        # Create info table
        data = [
            ['Translation Date:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Source Language:', metadata.get('source_language', 'Urdu').upper()],
            ['Target Language:', metadata.get('target_language', 'English').upper()],
            ['Translation Method:', metadata.get('method', 'Setu-Translate').title()],
            ['Confidence Score:', f"{metadata.get('confidence', 0) * 100:.1f}%"],
        ]
        
        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _add_original_section(self, original_data: Dict):
        """Add original text section"""
        elements = []
        
        # Section heading
        heading = Paragraph("ORIGINAL TEXT (URDU)", self.styles['CustomHeading'])
        elements.append(heading)
        
        # Original text
        text = original_data.get('cleaned_text', original_data.get('raw_text', ''))
        
        # Create text box
        text_para = Paragraph(
            self._escape_html(text),
            self.styles['CustomBody']
        )
        elements.append(text_para)
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _add_translated_section(self, translated_data: Dict):
        """Add translated text section"""
        elements = []
        
        # Section heading
        heading = Paragraph("TRANSLATED TEXT (ENGLISH)", self.styles['CustomHeading'])
        elements.append(heading)
        
        # Translated text
        text = translated_data.get('text', '')
        
        # Create text box with background
        text_para = Paragraph(
            self._escape_html(text),
            self.styles['CustomBody']
        )
        elements.append(text_para)
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _add_metadata_section(self, metadata: Dict):
        """Add metadata section"""
        elements = []
        
        # Section heading
        heading = Paragraph("TRANSLATION DETAILS", self.styles['CustomHeading'])
        elements.append(heading)
        
        # Metadata table
        data = []
        
        if 'original_length' in metadata:
            data.append(['Original Character Count:', str(metadata['original_length'])])
        
        if 'translated_length' in metadata:
            data.append(['Translated Character Count:', str(metadata['translated_length'])])
        
        if 'word_count' in metadata:
            data.append(['Word Count:', str(metadata['word_count'])])
        
        if data:
            table = Table(data, colWidths=[2.5 * inch, 3.5 * inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _add_footer(self):
        """Add PDF footer"""
        elements = []
        
        # Horizontal line
        elements.append(self._create_horizontal_line())
        elements.append(Spacer(1, 0.1 * inch))
        
        # Footer text
        footer_text = Paragraph(
            "<i>This translation was generated using the Land Owners OCR System "
            "as part of the J&K AgriStack Implementation initiative.</i>",
            self.styles['Normal']
        )
        elements.append(footer_text)
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>Note: While this translation strives for accuracy, "
            "it is recommended to verify critical information with official sources.</i>",
            ParagraphStyle(
                name='Disclaimer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#9ca3af'),
                alignment=TA_CENTER
            )
        )
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(disclaimer)
        
        return elements
    
    def _create_horizontal_line(self):
        """Create horizontal line"""
        line_data = [['']]
        line = Table(line_data, colWidths=[6.5 * inch])
        line.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#d1d5db')),
        ]))
        return line
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ''
        
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('\n', '<br/>')
        
        return text


def test_pdf_generator():
    """Test PDF generation"""
    generator = PDFGenerator()
    
    # Sample translation data
    sample_data = {
        'original': {
            'raw_text': 'جمع بندی موضع اتما پور تحصیل بشنال ضلع جموں',
            'cleaned_text': 'جمع بندی موضع اتما پور تحصیل بشنال ضلع جموں',
            'language': 'ur'
        },
        'translated': {
            'text': 'Jamabandi Village Atmapur Tehsil Bishnah District Jammu',
            'language': 'en'
        },
        'metadata': {
            'source_language': 'ur',
            'target_language': 'en',
            'confidence': 0.85,
            'method': 'setu-translate',
            'original_length': 48,
            'translated_length': 56
        }
    }
    
    # Generate PDF
    pdf_buffer = generator.generate_translation_pdf(sample_data)
    
    # Save to file
    with open('test_translation.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("PDF generated successfully: test_translation.pdf")


if __name__ == '__main__':
    test_pdf_generator()

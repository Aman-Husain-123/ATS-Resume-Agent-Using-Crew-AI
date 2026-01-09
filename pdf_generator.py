"""
PDF Resume Generator
Creates professional PDF resumes from text content
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO


def generate_pdf_resume(text_content):
    """
    Generate a professional PDF resume from text content
    
    Args:
        text_content: Resume text content
        
    Returns:
        bytes: PDF file content
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1f2937',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#374151',
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor='#1f2937',
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Parse content and add to PDF
    lines = text_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Add spacing for empty lines
            elements.append(Spacer(1, 0.1*inch))
            continue
        
        # Detect headings (all caps or specific patterns)
        if line.isupper() and len(line) < 50:
            # Main heading
            elements.append(Paragraph(line, title_style))
        elif line.startswith('#'):
            # Markdown-style heading
            clean_line = line.lstrip('#').strip()
            elements.append(Paragraph(clean_line, heading_style))
        elif line.endswith(':') and len(line) < 50:
            # Section heading
            elements.append(Paragraph(line, heading_style))
        else:
            # Regular text
            # Escape special characters for ReportLab
            safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(safe_line, body_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

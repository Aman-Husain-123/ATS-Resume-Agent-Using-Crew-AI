"""
File Loading and Text Extraction Tools
This module handles resume file uploads and text extraction from various formats.
Supports PDF, DOCX, and plain text files.
"""

import io
from typing import Tuple
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text content from PDF file.
    
    Uses pypdf library to read PDF and extract text from all pages.
    Handles multi-page resumes by concatenating page content.
    
    Args:
        file_bytes: PDF file content as bytes
        
    Returns:
        str: Extracted text from all pages, joined with newlines
        
    Note:
        - May not preserve exact formatting
        - Works best with text-based PDFs (not scanned images)
        - Empty pages return empty strings
    """
    # Create PDF reader from bytes
    reader = PdfReader(io.BytesIO(file_bytes))
    parts = []
    
    # Extract text from each page
    for page in reader.pages:
        txt = page.extract_text() or ""
        parts.append(txt)
    
    return "\n".join(parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text content from DOCX (Word) file.
    
    Uses python-docx library to read Word documents and extract paragraph text.
    Preserves paragraph structure but not formatting.
    
    Args:
        file_bytes: DOCX file content as bytes
        
    Returns:
        str: Extracted text from all paragraphs, joined with newlines
        
    Note:
        - Extracts only paragraph text (not headers, footers, tables)
        - Does not preserve formatting (bold, italic, etc.)
        - Empty paragraphs return empty strings
    """
    # Create document reader from bytes
    f = io.BytesIO(file_bytes)
    doc = Document(f)
    parts = []
    
    # Extract text from each paragraph
    for p in doc.paragraphs:
        parts.append(p.text)
    
    return "\n".join(parts)


def detect_and_extract(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Automatically detect file type and extract text content.
    
    Detects file type based on extension and routes to appropriate extractor.
    Supports PDF, DOCX, and plain text files with fallback handling.
    
    Args:
        filename: Original filename with extension (e.g., "resume.pdf")
        file_bytes: File content as bytes
        
    Returns:
        Tuple[str, str]: (file_extension, extracted_text)
            - file_extension: One of "pdf", "docx", "txt", or "bin" (unknown)
            - extracted_text: Text content extracted from file
            
    Example:
        >>> ext, text = detect_and_extract("resume.pdf", pdf_bytes)
        >>> print(f"Detected {ext} file with {len(text)} characters")
        Detected pdf file with 1234 characters
        
    Note:
        - Detection is case-insensitive
        - Unknown formats attempt UTF-8 decoding
        - Binary files return empty string
    """
    # Convert filename to lowercase for case-insensitive matching
    low = filename.lower()
    
    # Route to appropriate extractor based on extension
    if low.endswith(".pdf"):
        return "pdf", extract_text_from_pdf(file_bytes)
    
    if low.endswith(".docx"):
        return "docx", extract_text_from_docx(file_bytes)
    
    # Fallback: attempt to decode as plain text
    try:
        return "txt", file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        # Unknown binary format
        return "bin", ""

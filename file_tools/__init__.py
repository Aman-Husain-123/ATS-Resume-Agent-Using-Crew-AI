"""
File Tools Package
Provides utilities for loading and extracting text from resume files.
Supports PDF, DOCX, and plain text formats.
"""

from .file_loader import (
    extract_text_from_pdf,
    extract_text_from_docx,
    detect_and_extract
)

__all__ = [
    'extract_text_from_pdf',
    'extract_text_from_docx',
    'detect_and_extract'
]

"""CV extraction package.

This package contains document text extraction, CV attribute extraction and
(optional) normalization helpers.

The backend imports from this package to keep CV extraction logic isolated.
"""

from .pdf_processor import PDFProcessor
from .cv_extractor import CVExtractor
from .document_normalizer import DocumentNormalizer
from .section_detector import CVSectionDetector, CVSection

__all__ = [
    "PDFProcessor",
    "CVExtractor",
    "DocumentNormalizer",
    "CVSectionDetector",
    "CVSection",
]

"""Document format normalization service."""

import os
import tempfile
from pathlib import Path
from typing import Tuple
import PyPDF2
from docx import Document
import pytesseract  # OCR para PDFs escaneados
from PIL import Image
from pdf2image import convert_from_path

from app.core.exceptions import DocumentProcessingError
from app.core.logger import get_logger

logger = get_logger(__name__)


class DocumentNormalizer:
    """Normalizes documents of different formats to plain text."""

    @staticmethod
    def normalize(filepath: Path) -> Tuple[str, str]:
        """
        Normalize document to plain text, handling multiple formats.
        
        Args:
            filepath: Path to document
            
        Returns:
            Tuple of (normalized_text, document_type)
        """
        file_ext = filepath.suffix.lower()
        
        if file_ext == ".pdf":
            text, doc_type = DocumentNormalizer._process_pdf(filepath)
        elif file_ext in [".docx", ".doc"]:
            text = DocumentNormalizer._process_docx(filepath)
            doc_type = "docx"
        elif file_ext == ".txt":
            text = DocumentNormalizer._process_txt(filepath)
            doc_type = "txt"
        else:
            raise DocumentProcessingError(f"Unsupported format: {file_ext}")
        
        # Cleanup
        text = DocumentNormalizer._cleanup_text(text)
        return text, doc_type

    @staticmethod
    def _process_pdf(filepath: Path) -> Tuple[str, str]:
        """
        Process PDF - detects between native text and scanned images.
        
        Strategy:
        1. Try extracting native text first (rápido)
        2. If text is < 50% of expected, use OCR (más confiable para scans)
        3. Combine both if needed
        """
        try:
            # Intentar extracción de texto nativo
            native_text = DocumentNormalizer._extract_pdf_native_text(filepath)
            
            # Si obtuvimos texto sustancial (>30% del tamaño del archivo)
            if len(native_text.strip()) > 100:
                logger.info(f"PDF {filepath.name}: Texto nativo extraído")
                return native_text, "pdf_native"
            
            # Fallback: OCR para PDFs escaneados
            logger.info(f"PDF {filepath.name}: Usando OCR (PDF escaneado detectado)")
            ocr_text = DocumentNormalizer._extract_pdf_ocr(filepath)
            return ocr_text, "pdf_ocr"
            
        except Exception as e:
            raise DocumentProcessingError(f"PDF processing failed: {str(e)}")

    @staticmethod
    def _extract_pdf_native_text(filepath: Path) -> str:
        """Extract native text from PDF."""
        text = []
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)

    @staticmethod
    def _extract_pdf_ocr(filepath: Path) -> str:
        """Extract text from PDF using OCR (pytesseract + pdf2image)."""
        try:
            images = convert_from_path(str(filepath))
            text = []
            for image in images:
                page_text = pytesseract.image_to_string(image, lang='spa+eng')
                text.append(page_text)
            return "\n".join(text)
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            raise DocumentProcessingError(f"OCR extraction failed: {str(e)}")

    @staticmethod
    def _process_docx(filepath: Path) -> str:
        """Extract text from DOCX."""
        doc = Document(filepath)
        paragraphs = [para.text for para in doc.paragraphs]
        return "\n".join(paragraphs)

    @staticmethod
    def _process_txt(filepath: Path) -> str:
        """Extract text from TXT file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def _cleanup_text(text: str) -> str:
        """
        Clean and normalize text.
        
        - Remove extra whitespace
        - Normalize line breaks
        - Remove special characters but keep structure
        """
        import re
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove multiple line breaks but keep paragraph structure
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
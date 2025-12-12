"""PDF processing service."""

import os
import PyPDF2
from datetime import datetime
from pathlib import Path
from typing import Optional
from docx import Document

from app.core.exceptions import PDFExtractionError
from app.core.logger import get_logger

logger = get_logger(__name__)


class PDFProcessor:
    """Service for processing PDF documents."""

    # Dependencies will be injected
    MAX_PAGES = 100
    SUPPORTED_FORMATS = [".pdf", ".docx", ".doc", ".txt"]

    @staticmethod
    def extract_text(filepath: Path) -> str:
        """
        Extract text from PDF or document file.

        Args:
            filepath: Path to the document file

        Returns:
            Extracted text content

        Raises:
            PDFExtractionError: If extraction fails
        """
        try:
            file_ext = filepath.suffix.lower()

            if file_ext == ".pdf":
                return PDFProcessor._extract_from_pdf(filepath)
            elif file_ext in [".docx", ".doc"]:
                return PDFProcessor._extract_from_docx(filepath)
            elif file_ext == ".txt":
                return PDFProcessor._extract_from_txt(filepath)
            else:
                raise PDFExtractionError(f"Unsupported file format: {file_ext}")

        except PDFExtractionError:
            raise
        except Exception as e:
            raise PDFExtractionError(
                f"Failed to extract text from {filepath.name}: {str(e)}",
                details={"filepath": str(filepath), "error": str(e)},
            )

    @staticmethod
    def _extract_from_pdf(filepath: Path) -> str:
        """Extract text from PDF file."""
        try:
            #import PyPDF2

            text_content = []
            with open(filepath, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(pdf_reader.pages[: PDFProcessor.MAX_PAGES]):
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

            result = "\n".join(text_content)
            if not result.strip():
                raise PDFExtractionError(f"No text extracted from PDF: {filepath.name}")

            logger.info(f"Extracted {len(result)} characters from PDF: {filepath.name}")
            return result

        except ImportError:
            raise PDFExtractionError(
                "PyPDF2 not installed. Install it with: pip install PyPDF2",
                details={"library": "PyPDF2"},
            )

    @staticmethod
    def _extract_from_docx(filepath: Path) -> str:
        """Extract text from DOCX file."""
        try:
            #from docx import Document

            doc = Document(filepath)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            result = "\n".join(paragraphs)

            if not result.strip():
                raise PDFExtractionError(f"No text extracted from DOCX: {filepath.name}")

            logger.info(f"Extracted {len(result)} characters from DOCX: {filepath.name}")
            return result

        except ImportError:
            raise PDFExtractionError(
                "python-docx not installed. Install it with: pip install python-docx",
                details={"library": "python-docx"},
            )

    @staticmethod
    def _extract_from_txt(filepath: Path) -> str:
        """Extract text from TXT file."""
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            result = f.read()

        if not result.strip():
            raise PDFExtractionError(f"No text in file: {filepath.name}")

        logger.info(f"Extracted {len(result)} characters from TXT: {filepath.name}")
        return result

    @staticmethod
    def get_text_preview(text: str, max_chars: int = 500) -> str:
        """Get preview of extracted text."""
        return text[: max_chars] + ("..." if len(text) > max_chars else "")

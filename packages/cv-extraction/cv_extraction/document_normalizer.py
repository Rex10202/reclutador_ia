"""Document format normalization service.

This is currently not wired into the API flow, but kept here to centralize CV
text extraction (including optional OCR).
"""

from pathlib import Path
from typing import Tuple

from .exceptions import DocumentProcessingError
from .logging_utils import get_logger

logger = get_logger(__name__)


class DocumentNormalizer:
    """Normalizes documents of different formats to plain text."""

    @staticmethod
    def normalize(filepath: Path) -> Tuple[str, str]:
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

        text = DocumentNormalizer._cleanup_text(text)
        return text, doc_type

    @staticmethod
    def _process_pdf(filepath: Path) -> Tuple[str, str]:
        try:
            native_text = DocumentNormalizer._extract_pdf_native_text(filepath)

            if len(native_text.strip()) > 100:
                logger.info(f"PDF {filepath.name}: Texto nativo extraído")
                return native_text, "pdf_native"

            logger.info(f"PDF {filepath.name}: Usando OCR (PDF escaneado detectado)")
            ocr_text = DocumentNormalizer._extract_pdf_ocr(filepath)
            return ocr_text, "pdf_ocr"

        except DocumentProcessingError:
            raise
        except Exception as e:
            raise DocumentProcessingError(f"PDF processing failed: {str(e)}")

    @staticmethod
    def _extract_pdf_native_text(filepath: Path) -> str:
        try:
            import PyPDF2

            text = []
            with open(filepath, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text.append(extracted)
            return "\n".join(text)

        except ImportError as e:
            raise DocumentProcessingError(
                "PyPDF2 not installed. Install it with: pip install PyPDF2",
                details={"error": str(e)},
            )

    @staticmethod
    def _extract_pdf_ocr(filepath: Path) -> str:
        """Extract text from PDF using OCR (optional dependencies)."""
        try:
            import pytesseract  # type: ignore
            from pdf2image import convert_from_path  # type: ignore

            images = convert_from_path(str(filepath))
            text = []
            for image in images:
                page_text = pytesseract.image_to_string(image, lang="spa+eng")
                text.append(page_text)
            return "\n".join(text)

        except ImportError as e:
            raise DocumentProcessingError(
                "OCR dependencies not installed (pytesseract, pdf2image, pillow).",
                details={"error": str(e)},
            )
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            raise DocumentProcessingError(f"OCR extraction failed: {str(e)}")

    @staticmethod
    def _process_docx(filepath: Path) -> str:
        try:
            from docx import Document

            doc = Document(filepath)
            paragraphs = [para.text for para in doc.paragraphs]
            return "\n".join(paragraphs)

        except ImportError as e:
            raise DocumentProcessingError(
                "python-docx not installed. Install it with: pip install python-docx",
                details={"error": str(e)},
            )

    @staticmethod
    def _process_txt(filepath: Path) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _cleanup_text(text: str) -> str:
        import re

        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

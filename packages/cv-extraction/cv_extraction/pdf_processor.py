"""Document text extraction utilities (PDF/DOCX/TXT)."""

from pathlib import Path

from .exceptions import PDFExtractionError
from .logging_utils import get_logger

logger = get_logger(__name__)


class PDFProcessor:
    """Service for processing PDF and other document formats."""

    MAX_PAGES = 100
    SUPPORTED_FORMATS = [".pdf", ".docx", ".doc", ".txt"]

    @staticmethod
    def extract_text(filepath: Path) -> str:
        try:
            file_ext = filepath.suffix.lower()

            if file_ext == ".pdf":
                return PDFProcessor._extract_from_pdf(filepath)
            if file_ext in [".docx", ".doc"]:
                return PDFProcessor._extract_from_docx(filepath)
            if file_ext == ".txt":
                return PDFProcessor._extract_from_txt(filepath)

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
        try:
            import PyPDF2

            text_content = []
            with open(filepath, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages[: PDFProcessor.MAX_PAGES]:
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
        try:
            from docx import Document

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
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            result = f.read()

        if not result.strip():
            raise PDFExtractionError(f"No text in file: {filepath.name}")

        logger.info(f"Extracted {len(result)} characters from TXT: {filepath.name}")
        return result

    @staticmethod
    def get_text_preview(text: str, max_chars: int = 500) -> str:
        return text[: max_chars] + ("..." if len(text) > max_chars else "")

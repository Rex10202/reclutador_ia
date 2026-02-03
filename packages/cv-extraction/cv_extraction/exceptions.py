"""Exceptions for cv_extraction.

These mirror the backend exception intent without coupling the package to the
backend app package.
"""

from typing import Any, Dict, Optional


class DocumentProcessingError(Exception):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PDFExtractionError(DocumentProcessingError):
    pass

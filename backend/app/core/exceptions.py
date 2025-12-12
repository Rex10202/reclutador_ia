"""Custom exception classes for the application."""

from typing import Any, Dict, Optional


class ApplicationException(Exception):
    """Base exception for the application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ApplicationException):
    """Raised when data validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=400, error_code="VALIDATION_ERROR", details=details)


class DocumentProcessingError(ApplicationException):
    """Raised when document processing fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, status_code=422, error_code="DOCUMENT_PROCESSING_ERROR", details=details
        )


class PDFExtractionError(DocumentProcessingError):
    """Raised when PDF text extraction fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, details=details)
        self.error_code = "PDF_EXTRACTION_ERROR"


class NotAJobQueryError(ApplicationException):
    """Raised when query is not job-related."""

    def __init__(self, message: str = "Query is not job-related"):
        super().__init__(message=message, status_code=400, error_code="NOT_A_JOB_QUERY")


class NoCandidatesFoundError(ApplicationException):
    """Raised when no matching candidates are found."""

    def __init__(self, message: str = "No candidates found matching criteria"):
        super().__init__(message=message, status_code=404, error_code="NO_CANDIDATES_FOUND")


class ResourceNotFoundError(ApplicationException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with id {identifier} not found"
        super().__init__(message=message, status_code=404, error_code="RESOURCE_NOT_FOUND")


class InvalidFileFormatError(ValidationError):
    """Raised when file format is not supported."""

    def __init__(self, message: str, supported_formats: Optional[list] = None):
        details = {"supported_formats": supported_formats} if supported_formats else {}
        super().__init__(message=message, details=details)
        self.error_code = "INVALID_FILE_FORMAT"


class FileSizeExceededError(ValidationError):
    """Raised when file size exceeds limit."""

    def __init__(self, max_size_mb: float):
        message = f"File size exceeds maximum allowed size of {max_size_mb}MB"
        super().__init__(message=message, details={"max_size_mb": max_size_mb})
        self.error_code = "FILE_SIZE_EXCEEDED"

"""Input validation utilities."""

from app.core.exceptions import FileSizeExceededError, InvalidFileFormatError, ValidationError
from app.core.security import MAX_FILE_SIZE_MB, MAX_UPLOAD_FILES, ALLOWED_FORMATS, validate_file_extension, validate_file_size, validate_num_files


def validate_document_file(filename: str, file_size_bytes: int) -> None:
    """Validate uploaded file."""
    if not validate_file_extension(filename):
        raise InvalidFileFormatError(
            message=f"File format not supported: {filename}",
            supported_formats=list(ALLOWED_FORMATS),
        )

    if not validate_file_size(file_size_bytes):
        raise FileSizeExceededError(max_size_mb=MAX_FILE_SIZE_MB)


def validate_documents_count(num_files: int) -> None:
    """Validate number of uploaded documents."""
    if num_files < 2:
        raise ValidationError(
            message="Minimum 2 documents required for comparison",
            details={"min_documents": 2, "provided": num_files},
        )

    if num_files > MAX_UPLOAD_FILES:
        raise ValidationError(
            message=f"Maximum {MAX_UPLOAD_FILES} documents allowed",
            details={"max_documents": MAX_UPLOAD_FILES, "provided": num_files},
        )


def validate_insight_filters(filters: dict) -> None:
    """Validate insight filters configuration."""
    if not filters:
        raise ValidationError(message="At least one insight filter must be enabled")

    for filter_item in filters.get("filters", []):
        if "weight" in filter_item:
            weight = filter_item["weight"]
            if not (0.1 <= weight <= 10.0):
                raise ValidationError(
                    message=f"Filter weight must be between 0.1 and 10.0, got {weight}",
                    details={"filter_id": filter_item.get("filter_id"), "weight": weight},
                )

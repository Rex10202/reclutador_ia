"""Security utilities and validations."""

import os
from typing import Set


# File upload constraints
MAX_FILE_SIZE_MB = 50  # Maximum file size in MB
MAX_UPLOAD_FILES = 10  # Maximum files per request
ALLOWED_FORMATS: Set[str] = {".pdf", ".docx", ".doc", ".txt"}
UPLOAD_TEMP_DIR = os.getenv("UPLOAD_TEMP_DIR", "/tmp/uploads")


def validate_file_extension(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_FORMATS


def validate_file_size(file_size_bytes: int) -> bool:
    """Check if file size is within limits."""
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    return file_size_bytes <= max_bytes


def validate_num_files(num_files: int) -> bool:
    """Check if number of files is within limits."""
    return 2 <= num_files <= MAX_UPLOAD_FILES


def ensure_upload_dir_exists():
    """Ensure temporary upload directory exists."""
    os.makedirs(UPLOAD_TEMP_DIR, exist_ok=True)

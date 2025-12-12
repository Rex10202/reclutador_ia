"""File handling utilities."""

import os
import uuid
from pathlib import Path
from typing import Optional

from app.core.logger import get_logger
from app.core.security import UPLOAD_TEMP_DIR, ensure_upload_dir_exists

logger = get_logger(__name__)


def generate_document_id() -> str:
    """Generate unique document ID."""
    return str(uuid.uuid4())


def get_upload_path(filename: str, document_id: Optional[str] = None) -> Path:
    """Get path where file should be saved."""
    ensure_upload_dir_exists()
    if document_id is None:
        document_id = generate_document_id()

    upload_path = Path(UPLOAD_TEMP_DIR) / document_id
    upload_path.mkdir(parents=True, exist_ok=True)

    return upload_path / filename


def save_uploaded_file(file_content: bytes, filename: str, document_id: str) -> Path:
    """Save uploaded file and return its path."""
    filepath = get_upload_path(filename, document_id)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "wb") as f:
        f.write(file_content)

    logger.info(f"Saved file: {filepath}")
    return filepath


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes."""
    return filepath.stat().st_size


def cleanup_document_files(document_id: str) -> bool:
    """Remove all files associated with a document."""
    doc_path = Path(UPLOAD_TEMP_DIR) / document_id
    if doc_path.exists():
        import shutil

        shutil.rmtree(doc_path)
        logger.info(f"Cleaned up document files: {doc_path}")
        return True
    return False

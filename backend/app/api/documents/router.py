"""Document processing endpoints."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.exceptions import ApplicationException
from app.core.logger import get_logger
from app.models.schemas import CVAnalysisResponse, ExtractedAttribute
from app.services.cv_extractor import CVExtractor
from app.services.pdf_processor import PDFProcessor
from app.utils.file_handler import generate_document_id, save_uploaded_file, get_file_size
from app.utils.validators import validate_document_file, validate_documents_count

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/upload",
    response_model=List[CVAnalysisResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and analyze CV documents",
    description="Upload 2-10 PDF/DOCX documents for analysis. Extracts text and analyzes attributes.",
)
async def upload_documents(files: List[UploadFile] = File(..., description="List of CV files to upload")):
    """
    Upload and analyze multiple CV documents.

    - **files**: List of 2-10 PDF, DOCX, or TXT files
    - **Returns**: List of analysis results for each document

    **Validation rules:**
    - Minimum 2 files, maximum 10 files
    - Supported formats: PDF, DOCX, DOC, TXT
    - Maximum file size: 50MB per file
    """
    try:
        # Validate number of files
        validate_documents_count(len(files))

        results = []

        for file in files:
            try:
                # Validate file
                file_content = await file.read()
                validate_document_file(file.filename, len(file_content))

                # Save file
                document_id = generate_document_id()
                filepath = save_uploaded_file(file_content, file.filename, document_id)

                # Extract text from document
                raw_text = PDFProcessor.extract_text(filepath)
                text_preview = PDFProcessor.get_text_preview(raw_text)

                # Extract attributes from CV
                attributes = CVExtractor.extract_attributes(raw_text, document_id)

                result = CVAnalysisResponse(
                    document_id=document_id,
                    filename=file.filename,
                    status="success",
                    extracted_attributes=attributes,
                    raw_text_preview=text_preview,
                    processing_time_ms=0.0,  # TODO: Add timing
                )

                results.append(result)
                logger.info(f"Successfully analyzed document: {file.filename}")

            except ApplicationException as e:
                result = CVAnalysisResponse(
                    document_id="",
                    filename=file.filename,
                    status="error",
                    error_message=e.message,
                    processing_time_ms=0.0,
                )
                results.append(result)
                logger.error(f"Error analyzing {file.filename}: {e.message}")

        return results

    except ApplicationException as e:
        logger.error(f"Document upload error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail={"error": e.error_code, "message": e.message})

    except Exception as e:
        logger.error(f"Unexpected error in upload_documents: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "INTERNAL_ERROR", "message": str(e)})


@router.get(
    "/{document_id}",
    response_model=CVAnalysisResponse,
    summary="Get document analysis details",
    description="Retrieve previously analyzed document with all extracted attributes.",
)
async def get_document_analysis(document_id: str):
    """
    Get analysis details for a specific document.

    - **document_id**: ID of previously uploaded document
    - **Returns**: Document analysis with extracted attributes
    """
    # TODO: Implement document retrieval from storage/cache
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Remove document and associated analysis data.",
)
async def delete_document(document_id: str):
    """
    Delete a document and its analysis.

    - **document_id**: ID of document to delete
    """
    # TODO: Implement document deletion
    raise HTTPException(status_code=501, detail="Not implemented yet")

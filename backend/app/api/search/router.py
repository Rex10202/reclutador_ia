"""Search and natural language query endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import ApplicationException
from app.core.logger import get_logger
from app.models.schemas import SearchQueryRequest, SearchResponse

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search by natural language",
    description="Fallback endpoint for natural language queries when CV matching doesn't find results.",
)
async def search_candidates(query: SearchQueryRequest):
    """
    Search candidates using natural language query.

    This is the Module 2 fallback - when CV analysis doesn't find matching profiles,
    recruiters can use natural language to search across platforms.

    - **text**: Natural language query (e.g., "Ingeniero de software con 5 años en Python y React")
    - **Returns**: List of ranked candidates

    **Note**: This endpoint maintains compatibility with the existing `/query` endpoint.
    """
    try:
        # TODO: Integrate with existing query_pipeline.py
        # This will use:
        # - job_query_filter.py to validate it's a job query
        # - NLP parser to extract structured requirements
        # - ranking_model to score candidates from database

        logger.info(f"Processing search query: {query.text}")

        # Placeholder response structure
        raise HTTPException(status_code=501, detail="Search endpoint not fully implemented yet")

    except ApplicationException as e:
        logger.error(f"Search error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail={"error": e.error_code, "message": e.message})

    except Exception as e:
        logger.error(f"Unexpected error in search_candidates: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "INTERNAL_ERROR", "message": str(e)})


@router.get(
    "/health",
    summary="Health check for search module",
    status_code=status.HTTP_200_OK,
)
async def search_health():
    """Check if search module is operational."""
    return {"status": "ok", "module": "search"}

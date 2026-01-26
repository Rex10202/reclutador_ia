"""API router aggregator."""

from fastapi import APIRouter

from app.api.documents.router import router as documents_router
from app.api.search.router import router as search_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(search_router, prefix="/search", tags=["search"])

__all__ = ["api_router"]

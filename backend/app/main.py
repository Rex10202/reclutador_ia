"""Main FastAPI application factory."""

from datetime import datetime
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.config import settings
from app.core.exceptions import ApplicationException
from app.core.logger import get_logger
from app.models.schemas import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    # Exception handlers
    @app.exception_handler(ApplicationException)
    async def application_exception_handler(request: Request, exc: ApplicationException):
        """Handle custom application exceptions."""
        logger.error(f"Application exception: {exc.message} (Code: {exc.error_code})")
        error_detail = ErrorDetail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details if exc.details else None,
        )
        response = ErrorResponse(
            error=error_detail,
            timestamp=datetime.utcnow(),
            path=str(request.url.path),
        )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error on {request.method} {request.url.path}")
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(x) for x in error["loc"][1:]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        error_detail = ErrorDetail(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": errors},
        )
        response = ErrorResponse(
            error=error_detail,
            timestamp=datetime.utcnow(),
            path=str(request.url.path),
        )
        return JSONResponse(status_code=400, content=response.model_dump())

    # Health check endpoints
    @app.get("/health", tags=["health"])
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok", "service": "reclutador_ia_backend"}

    @app.get("/health/ready", tags=["health"])
    async def readiness_check() -> Dict[str, str]:
        """Readiness check endpoint."""
        return {"ready": True, "timestamp": datetime.utcnow().isoformat()}

    # Include API routers
    app.include_router(api_router)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> Dict[str, str]:
        """Root endpoint with API information."""
        return {
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "docs": "/docs",
            "status": "running",
        }

    logger.info(f"FastAPI application created: {settings.API_TITLE} v{settings.API_VERSION}")
    return app


# Create application instance
app = create_app()

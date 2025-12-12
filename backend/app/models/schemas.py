"""Pydantic schemas and data models for request/response validation."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# DOCUMENT UPLOAD & ANALYSIS SCHEMAS
# ============================================================================


class DocumentMetadata(BaseModel):
    """Metadata for uploaded document."""

    document_id: str
    filename: str
    upload_date: datetime
    file_size_bytes: int


class ExtractedAttribute(BaseModel):
    """Single extracted attribute from CV."""

    attribute_type: str  # e.g., "skill", "role", "experience_years"
    value: str
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    source_text: Optional[str] = None  # Text snippet where it was found


class CVAnalysisResponse(BaseModel):
    """Analysis result of a single CV."""

    document_id: str
    filename: str
    status: str  # "success", "error"
    extracted_attributes: List[ExtractedAttribute] = []
    raw_text_preview: Optional[str] = None
    error_message: Optional[str] = None
    processing_time_ms: float


# ============================================================================
# INSIGHT FILTERS SCHEMAS
# ============================================================================


class InsightFilter(BaseModel):
    """Individual insight filter for matching."""

    filter_id: str
    name: str  # e.g., "experience_years", "technical_skills", "education"
    enabled: bool
    weight: float = Field(default=1.0, ge=0.1, le=10.0, description="Weight for matching algorithm")
    config: Optional[Dict] = None  # Filter-specific configuration


class InsightFiltersRequest(BaseModel):
    """Request body for setting insight filters."""

    filters: List[InsightFilter]


class InsightFiltersResponse(BaseModel):
    """Response confirming filters were saved."""

    session_id: str
    filters: List[InsightFilter]
    updated_at: datetime


# ============================================================================
# MATCHING & COMPARISON SCHEMAS
# ============================================================================


class MatchScore(BaseModel):
    """Match score for a specific criterion."""

    criterion: str  # e.g., "technical_skills", "years_experience"
    score: float = Field(ge=0, le=100, description="Match percentage 0-100")
    details: Optional[Dict] = None


class CVMatchingResult(BaseModel):
    """Matching result between CV and job requirements."""

    document_id: str
    filename: str
    overall_score: float = Field(ge=0, le=100)
    scores_breakdown: List[MatchScore]
    matched_attributes: Dict[str, str]
    gaps: List[str]  # Attributes not matching requirements
    rank: int


class ComparisonResponse(BaseModel):
    """Response with all CVs matched and ranked."""

    session_id: str
    job_requirements: Dict  # Parsed job description
    results: List[CVMatchingResult]
    total_candidates_analyzed: int
    analysis_date: datetime


# ============================================================================
# SEARCH (NL FALLBACK) SCHEMAS
# ============================================================================


class SearchQueryRequest(BaseModel):
    """Natural language search query."""

    text: str = Field(..., min_length=3, max_length=500)


class ParsedQuery(BaseModel):
    """Structured query parsed from natural language."""

    role: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    location: Optional[str] = None
    languages: List[str] = []


class SearchCandidate(BaseModel):
    """Candidate result from search."""

    id: str
    role: str
    score: float = Field(ge=0, le=1)
    location: str
    years_experience: int
    languages: str
    skills: str


class SearchResponse(BaseModel):
    """Response for natural language search."""

    candidates: List[SearchCandidate]
    parsed_query: ParsedQuery
    total_results: int


# ============================================================================
# ERROR RESPONSE SCHEMAS
# ============================================================================


class ErrorDetail(BaseModel):
    """Error details in response."""

    error_code: str
    message: str
    details: Optional[Dict] = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorDetail
    timestamp: datetime
    path: Optional[str] = None

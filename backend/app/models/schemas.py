"""Pydantic schemas and data models for request/response validation."""

from datetime import datetime
from typing import Dict, List, Optional, Any

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
    warnings: List[str] = []
    error_message: Optional[str] = None
    processing_time_ms: float


# ============================================================================
# JOB REQUIREMENTS & FILTERS (Frontend Match)
# ============================================================================

class JobRequirements(BaseModel):
    title: str
    description: Optional[str] = None
    requiredSkills: List[str] = []
    preferredSkills: List[str] = []
    minExperience: int = 0
    maxExperience: Optional[int] = None
    location: Optional[str] = None
    languages: Optional[List[str]] = []
    education: Optional[List[str]] = []

class InsightFilters(BaseModel):
    prioritizeExperience: bool
    prioritizeSkills: bool
    prioritizeLocation: bool
    prioritizeLanguages: bool
    prioritizeEducation: bool
    prioritizeCertifications: bool

class AnalyzeDocumentsRequest(BaseModel):
    documentIds: List[str]
    jobRequirements: JobRequirements
    filters: InsightFilters

# ============================================================================
# ANALYSIS RESPONSE SCHEMAS
# ============================================================================

class MatchBreakdown(BaseModel):
    skillsMatch: float
    experienceMatch: float
    locationMatch: float
    languagesMatch: float
    educationMatch: float

class ExtractedAttributesSimple(BaseModel):
    candidateName: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    role: str
    yearsExperience: Optional[int] = None
    skills: List[str]
    languages: List[str]
    education: List[str]
    certifications: List[str]
    summary: Optional[str] = None

class ComparisonResult(BaseModel):
    documentId: str
    candidateName: str
    attributes: ExtractedAttributesSimple
    overallScore: float
    matchBreakdown: MatchBreakdown
    matchedSkills: List[str]
    missingSkills: List[str]
    highlights: List[str]
    concerns: List[str]
    warnings: List[str] = []

class SkillCount(BaseModel):
    skill: str
    count: int

class LocationCount(BaseModel):
    location: str
    count: int

class TalentSummary(BaseModel):
    totalCandidates: int
    matchesByRole: int
    averageExperience: float
    topSkills: List[SkillCount]
    locationDistribution: List[LocationCount]

class AnalyzeDocumentsResponse(BaseModel):
    results: List[ComparisonResult]
    summary: TalentSummary


# ============================================================================
# SEARCH SCHEMAS (Restaurados para evitar ImportError)
# ============================================================================

class SearchQueryRequest(BaseModel):
    """Request body for natural language search."""
    text: str = Field(..., min_length=3, description="Natural language query text")
    limit: int = Field(default=10, ge=1, le=50)

class Candidate(BaseModel):
    """Candidate model for search results."""
    id: str
    name: str
    role: str
    score: float
    location: str
    years_experience: int
    skills: str  # Semicolon separated
    languages: str  # Semicolon separated

class SearchResponse(BaseModel):
    """Response for search query."""
    query: str
    candidates: List[Candidate]
    total_results: int
    processing_time_ms: float

# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorDetail(BaseModel):
    """Standard error detail structure."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Standard API error response."""
    error: ErrorDetail
    timestamp: datetime
    path: str
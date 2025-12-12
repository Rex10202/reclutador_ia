"""Matching and ranking engine service."""

from typing import Dict, List

from app.core.logger import get_logger
from app.models.schemas import CVMatchingResult, MatchScore

logger = get_logger(__name__)


class MatchingEngine:
    """Service for matching CVs against job requirements."""

    # Will integrate with existing ranking_model
    DEFAULT_WEIGHTS = {
        "technical_skills": 2.0,
        "years_experience": 1.5,
        "education": 1.0,
        "languages": 0.8,
        "location": 1.0,
    }

    @staticmethod
    def compute_matching_scores(
        cv_attributes: Dict[str, str],
        job_requirements: Dict[str, str],
        insight_filters: Dict[str, float],
    ) -> CVMatchingResult:
        """
        Compute matching scores between CV and job requirements.

        Args:
            cv_attributes: Extracted attributes from CV
            job_requirements: Job description requirements
            insight_filters: Enabled filters with weights

        Returns:
            Matching result with overall and breakdown scores
        """
        try:
            # TODO: Integrate with existing ranking_model
            # This will use the semantic ranking engine already in place

            scores_breakdown = []
            total_score = 0
            total_weight = 0

            for criterion, weight in insight_filters.items():
                score = MatchingEngine._compute_criterion_score(cv_attributes, job_requirements, criterion)
                scores_breakdown.append(MatchScore(criterion=criterion, score=score, details={}))
                total_score += score * weight
                total_weight += weight

            overall_score = (total_score / total_weight) if total_weight > 0 else 0

            gaps = MatchingEngine._identify_gaps(cv_attributes, job_requirements, insight_filters)

            logger.info(f"Computed matching score: {overall_score:.2f}")
            return CVMatchingResult(
                document_id="",  # Will be set by caller
                filename="",  # Will be set by caller
                overall_score=min(overall_score, 100),
                scores_breakdown=scores_breakdown,
                matched_attributes=cv_attributes,
                gaps=gaps,
                rank=0,  # Will be set during ranking
            )

        except Exception as e:
            logger.error(f"Error computing matching scores: {str(e)}")
            raise

    @staticmethod
    def _compute_criterion_score(
        cv_attributes: Dict[str, str], job_requirements: Dict[str, str], criterion: str
    ) -> float:
        """
        Compute score for individual criterion.

        Args:
            cv_attributes: CV attributes dictionary
            job_requirements: Job requirements dictionary
            criterion: Criterion name

        Returns:
            Score 0-100
        """
        # TODO: Use semantic similarity (sentence-transformers)
        # and lexical matching from existing ranking_model

        cv_value = cv_attributes.get(criterion, "").lower()
        req_value = job_requirements.get(criterion, "").lower()

        if not cv_value or not req_value:
            return 0.0

        # Placeholder: simple substring matching
        if cv_value in req_value or req_value in cv_value:
            return 100.0

        return 50.0  # Partial match

    @staticmethod
    def _identify_gaps(
        cv_attributes: Dict[str, str], job_requirements: Dict[str, str], filters: Dict[str, float]
    ) -> List[str]:
        """Identify missing or mismatched attributes."""
        gaps = []

        for requirement_key in filters.keys():
            cv_value = cv_attributes.get(requirement_key, "").strip()
            if not cv_value:
                gaps.append(f"Missing: {requirement_key}")

        return gaps

    @staticmethod
    def rank_candidates(matching_results: List[CVMatchingResult]) -> List[CVMatchingResult]:
        """Rank candidates by overall score."""
        ranked = sorted(matching_results, key=lambda x: x.overall_score, reverse=True)

        for rank, result in enumerate(ranked, 1):
            result.rank = rank

        return ranked
